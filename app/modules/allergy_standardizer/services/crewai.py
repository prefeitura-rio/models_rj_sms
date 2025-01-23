import os
import json

from loguru import logger
from crewai import Agent, Crew, Task, LLM

from app.modules.allergy_standardizer.models import DataList
from app.modules.allergy_standardizer.config import (
    GEMINI_API_KEY,
    BATCH_SIZE
)


async def standardize_allergies_using_gemini(
    allergies_list: list,
):
    ### Defining gemini crew
    llm = LLM(
        model="gemini/gemini-pro",
        temperature=0.9,
        api_key=GEMINI_API_KEY,
    )

    buscador = Agent(
        llm=llm,
        role="Especialista de alergias",
        goal="Compreender os elementos causadores de alergia a um paciente, fazendo correções de grafia  nos inputs se necessário.",
        backstory="Você trabalha em uma unidade de saúde onde o preenchimento do "
        "campo de alergias no prontuario de pacientes tem diversos erros "
        "de digitação e mal preenchimento. Sua função é compreender e tratar "
        "as alergias inputadas descartando elementos que não se referirem a alergias."
        "Sempre que você nao estiver certo que um elemento se refere a uma alergia se pergunte se "
        "o elemento pode gerar uma alergia em uma pessoa, sabendo que as alergias podem se tratar de medicamentos, alimentos ou substâncias.",
        verbose=False,
    )

    limpeza = Task(
        description=(
            "1. Observe o input {alergias} e compreenda os causadores de alergias dentro do input. "
            "O input pode ser diretamente o termo que causa alergia ou uma frase contendo um termo que causa alergia. Os causadores de alergia são "
            "alimentos, medicamentos ou substâncias que podem estar com grafia incorreta. \n"
            "2. Faça uma tratamento no input corrigindo a grafia dos elementos. Elementos que nao causam alergias são definidos como tudo "
            "o que não se trata de medicamentos, alimentos ou substâncias e devem ser retornados com output sendo uma string vazia "
            ". \n"
            "3. O que você não tenha certeza do que se trata deve ser retornados com output sendo uma string vazia "
            " \n"
            "3. Retorne a lista de alergias \n"
        ),
        expected_output='Lista limpa cujos elementos são as alergias com grafia correta e que correspondem aos da lista input. Objeto JSON no formato {{"correcoes":{{"input":"alergia 1","output":"alergia limpa 1","motivo":"motivo do preenchimento do output"}},{{"input":"alergia 2","output":"alergia limpa 2","motivo":"motivo do preenchimento do output sem vírgulas"}}}}',
        agent=buscador,
        output_json=DataList
    )
    crew = Crew(
        agents=[buscador],
        tasks=[limpeza],
        verbose=True,
        memory=False
    )
    
    result_list = []
    for i in range(0, len(allergies_list), BATCH_SIZE):
        print(f"Batch {i} of {len(allergies_list)}")
        batch = allergies_list[i : i + BATCH_SIZE]

        result = await crew.kickoff_async(inputs={"alergias": str(batch)})

        try:
            resultado = result.json_dict['correcoes']
        except:
            resultado = len(batch) * [None]
        
        result_list.extend(resultado)

    return result_list
