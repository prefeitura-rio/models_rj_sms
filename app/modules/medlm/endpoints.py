import aiohttp
import json
from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends, HTTPException

from app.utils.authentication import decode_token
from app.utils.googlecloud import get_access_token
from app.config import SMS_PROJECT_ID
from app.modules.medlm.models import MedLMInput, MedLMOutput

router = APIRouter()

@router.post("/medlm/prompt")
async def prompt_medlm(
    input: MedLMInput,
    jwt_payload: Annotated[str, Depends(decode_token)],
) -> MedLMOutput:
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{SMS_PROJECT_ID}/locations/us-central1/publishers/google/models/{input.model}:predict"
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "instances": [dict(instance) for instance in input.instances],
        "parameters": dict(input.parameters) if input.parameters else None
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=500) as response:
                if response.status != 200:
                    error_detail = await response.text()
                    raise HTTPException(status_code=500, detail=f"HTTP error: {response.status} - {error_detail}")
                
                result = await response.json()
                return MedLMOutput(**result)

    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Client error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
