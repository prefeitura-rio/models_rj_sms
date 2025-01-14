import os
import json
import re
import requests

import pandas as pd
from loguru import logger

from app.utils.googlecloud import get_access_token
from app.config import SMS_PROJECT_ID


def predict(command: str):
    result = requests.post(
        url=f"https://us-central1-aiplatform.googleapis.com/v1/projects/{SMS_PROJECT_ID}/locations/us-central1/publishers/google/models/medlm-large:predict",
        headers={
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json; charset=utf-8"
        },
        data=json.dumps({
            "instances": [
                {
                    "content": command
                }
            ],
            "parameters": {
                "temperature": 0,
                "maxOutputTokens": 256,
                "topK": 40,
                "topP": 0.95
            }
        })
    )
    result.raise_for_status()

    return result.json()


def verify_results_using_medlm(
    gemini_result: list
):
    clean_mapping = []
    for result in gemini_result:
        i = result["input"]
        o = result["output"]
        if i == o:
            clean_mapping.append(
                {"input": i, "output": o, "output_medlm": {"flag": 1, "motivo": "Mesmo elemento"}}
            )
        elif o != "":
            response = predict(
                f"""
            Você receberá duas entradas que devem se tratar de causadores de alergia, ou seja, medicamento, classe de medicamentos, substâncias ou alimentos.
            Avalie se o input {i}, que possivelmente está escrito de forma errada, e o output {o} se referem ao mesmo causador de alergia.
            Caso um seja uma generalização do outro considere que são a mesma coisa.
            Ex: AINES e Cetoprofeno
            Retorne flag 1 caso verdadeiro e 0 caso falso. A saída deverá ter a explicação da resposta em um JSON válido no formato:
            {{"flag": Flag associada, "motivo": Explicação sucinta e sem vírgulas do valor associado a flag}}""",
            )
            json_str = re.search("{.*\n*.*}", response.text, re.IGNORECASE).group()
            json_str = json_str.replace("\n", " ")
            response = json.loads(json_str)

            clean_mapping.append({"input": i, "output": o, "output_medlm": response})
        elif o == "":
            response = predict(
                f"""
            Você receberá um input que possivelmente está escrito de forma errada.
            Avalie se o input {i} se refere a um causador de alergia. Pode ser um alimento, medicamento ou substância.
            Ex: 'AINES', 'Alergia a Cetoprofeno'
            Retorne flag 0 caso verdadeiro e 1 caso falso. A saída deverá ter a explicação da resposta em um JSON válido no formato:
            {{"flag": Flag associada, "motivo": Explicação sucinta e sem vírgulas do valor associado a flag}}""",
            )
            json_str = re.search("{.*\n*.*}", response.text, re.IGNORECASE).group()
            json_str = json_str.replace("\n", " ")
            response = json.loads(json_str)

            clean_mapping.append({"input": i, "output": o, "output_medlm": response})
    clean_mapping_df = pd.json_normalize(clean_mapping)
    clean_mapping_df.loc[clean_mapping_df["output_medlm.flag"] == 0, "output"] = (
        clean_mapping_df.loc[clean_mapping_df["output_medlm.flag"] == 0, "input"]
    )
    clean_mapping_df["output"] = clean_mapping_df["output"].str.replace("/", ",")
    clean_mapping_df["output"] = clean_mapping_df["output"].str.replace("\n", ",")

    return clean_mapping_df.to_dict(orient="records")