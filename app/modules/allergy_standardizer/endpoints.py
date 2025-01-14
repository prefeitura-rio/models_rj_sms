import json

from fastapi import APIRouter, HTTPException
from app.modules.allergy_standardizer.services.crewai import standardize_allergies_using_gemini
from app.modules.allergy_standardizer.services.medlm import verify_results_using_medlm
from app.modules.allergy_standardizer.models import AllergyStandardizeInput, AllergyStandardizeOutput
router = APIRouter()


@router.post("/allergy/standardize", tags=["standardizer"])
async def allergy_standardize(
    allergies_list: AllergyStandardizeInput,
) -> AllergyStandardizeOutput:
    gemini_result = standardize_allergies_using_gemini(
        allergies_list=allergies_list
    )

    verified_results = verify_results_using_medlm(
        gemini_result=gemini_result
    )

    return AllergyStandardizeOutput(results=verified_results)
