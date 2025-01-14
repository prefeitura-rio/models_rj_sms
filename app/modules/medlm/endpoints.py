import requests
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
    
    try:
        result = requests.post(
            url=f"https://us-central1-aiplatform.googleapis.com/v1/projects/{SMS_PROJECT_ID}/locations/us-central1/publishers/google/models/{input.model}:predict",
            headers={
                "Authorization": f"Bearer {get_access_token()}",
                "Content-Type": "application/json; charset=utf-8"
            },
            data=json.dumps({
                "instances": [dict(instance) for instance in input.instances],
                "parameters": dict(input.parameters) if input.parameters else None
            }),
            timeout=500
        )
        result.raise_for_status()
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=500, detail="Timeout while waiting for MedLM response")
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"HTTP error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

    return MedLMOutput(result.json())