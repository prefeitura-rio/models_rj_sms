import os
import json
import re
import aiohttp
import asyncio

import pandas as pd
from loguru import logger

from app.utils.googlecloud import get_access_token
from app.modules.medlm.models import MedLMOutput
from app.config import SMS_PROJECT_ID
from app.modules.allergy_standardizer.config import MEDLM_REQUEST_BATCH_SIZE


async def predict(commands: list[str]):
    """
    Perform batch predictions asynchronously using MedLM in smaller batches.

    :param commands: List of command strings to predict.
    :param MEDLM_REQUEST_BATCH_SIZE: Number of commands to process in each batch.
    :return: List of predictions corresponding to each command.
    """
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{SMS_PROJECT_ID}/locations/us-central1/publishers/google/models/medlm-large:predict"
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json; charset=utf-8"
    }

    async def fetch_prediction(session, command):
        """Helper function to send a single prediction request."""
        payload = {
            "instances": [
                {"content": command}
            ],
            "parameters": {
                "temperature": 0,
                "maxOutputTokens": 256,
                "topK": 40,
                "topP": 0.95
            }
        }

        async with session.post(url, headers=headers, json=payload) as response:
            try:
                response.raise_for_status()
            except Exception as e:
                logger.error(f"Error using MedLM: Status Code {response.status} - {await response.text()}")
                return None

            result = await response.json()
            data = MedLMOutput(**result)
            return data.predictions[0].content

    async def process_batch(session, batch):
        """Process a single batch of commands."""
        tasks = [fetch_prediction(session, command) for command in batch]
        return await asyncio.gather(*tasks, return_exceptions=True)

    results = []
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(commands), MEDLM_REQUEST_BATCH_SIZE):
            batch = commands[i:i + MEDLM_REQUEST_BATCH_SIZE]
            batch_results = await process_batch(session, batch)
            results.extend(batch_results)

    return results



async def verify_results_using_medlm(
    gemini_result: list
):
    verifications = {
        "equality": [],
        "empty_output": [],
        "not_empty_output": []
    }
    for result in gemini_result:
        if result["input"] == result["output"]:
            verifications["equality"].append(result)
        elif result["output"] != "":
            verifications["not_empty_output"].append(result)
        elif result["output"] == "":
            verifications["empty_output"].append(result)

        
    # ----------------------------
    # PREPARING COMMANDS
    # ----------------------------
    commands = []

    # Case: NOT_EMPTY_OUTPUT
    for verification in verifications["not_empty_output"]:
        commands.append(
            f"""
            Você receberá duas entradas que devem se tratar de causadores de alergia, ou seja, medicamento, classe de medicamentos, substâncias ou alimentos.
            Avalie se o input {verification["input"]}, que possivelmente está escrito de forma errada, e o output {verification["output"]} se referem ao mesmo causador de alergia.
            Caso um seja uma generalização do outro considere que são a mesma coisa.
            Ex: AINES e Cetoprofeno
            Retorne flag 1 caso verdadeiro e 0 caso falso. A saída deverá ter a explicação da resposta em um JSON válido no formato:
            {{"flag": Flag associada, "motivo": Explicação sucinta e sem vírgulas do valor associado a flag}}"""
        )

    # Case: EMPTY_OUTPUT
    for verification in verifications["empty_output"]:
        commands.append(
            f"""
            Você receberá um input que possivelmente está escrito de forma errada.
            Avalie se o input {verification["input"]} se refere a um causador de alergia. Pode ser um alimento, medicamento ou substância.
            Ex: 'AINES', 'Alergia a Cetoprofeno'
            Retorne flag 0 caso verdadeiro e 1 caso falso. A saída deverá ter a explicação da resposta em um JSON válido no formato:
            {{"flag": Flag associada, "motivo": Explicação sucinta e sem vírgulas do valor associado a flag}}"""
        )

    # ----------------------------
    # RUNNING PREDICTIONS
    # ----------------------------
    results = await predict(commands)
    
    not_empty_outputs_results = results[: len(verifications["not_empty_output"])]
    empty_outputs_results = results[len(verifications["not_empty_output"]) :]

    # ----------------------------
    # CALCULATING RESULTS
    # ----------------------------
    def clean_results(result):
        json_str = re.search("{.*\n*.*}", result, re.IGNORECASE).group()
        json_str = json_str.replace("\n", " ")
        result_as_json = json.loads(json_str)
        return result_as_json
    
    # Case: EQUALITY
    for verification in verifications["equality"]:
        verification["output_medlm"] = {
            "flag": 1,
            "motivo": "Mesmo elemento"
        }
    
    # Case: EMPTY_OUTPUT
    for i, result in enumerate(not_empty_outputs_results):
        verifications["not_empty_output"][i]["output_medlm"] = clean_results(result)
    
    # Case: NOT_EMPTY_OUTPUT
    for i, result in enumerate(empty_outputs_results):
        verifications["empty_output"][i]["output_medlm"] = clean_results(result)

    # ----------------------------
    # JOINING
    # ----------------------------
    all_results = \
        verifications["equality"] + \
        verifications["empty_output"] + \
        verifications["not_empty_output"]

    all_results_df = pd.json_normalize(all_results, sep="_")
    all_results_df.loc[all_results_df["output_medlm_flag"] == 0, "output"] = (
        all_results_df.loc[all_results_df["output_medlm_flag"] == 0, "input"]
    )
    all_results_df["output"] = all_results_df["output"].str.replace("/", ",")
    all_results_df["output"] = all_results_df["output"].str.replace("\n", ",")

    return all_results_df.to_dict(orient="records")