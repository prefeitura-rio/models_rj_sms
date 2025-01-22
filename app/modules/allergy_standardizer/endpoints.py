from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends

from app.modules.allergy_standardizer.services.crewai import standardize_allergies_using_gemini
from app.modules.allergy_standardizer.services.medlm import verify_results_using_medlm
from app.modules.allergy_standardizer.models import AllergyStandardizeInput, AllergyStandardizeOutput
from app.utils.authentication import decode_token


router = APIRouter()


@router.post("/allergy/standardize")
async def allergy_standardize(
    allergies_input: AllergyStandardizeInput,
    jwt_payload: Annotated[str, Depends(decode_token)],
) -> AllergyStandardizeOutput:
    
    
    # ------------------------------
    # Standardize allergies using Gemini
    # ------------------------------
    gemini_result = await standardize_allergies_using_gemini(
        allergies_list=allergies_input.allergies_list[:30]
    )

    # ------------------------------
    # Verify results using MedLM
    # ------------------------------
    verified_results = await verify_results_using_medlm(
        gemini_result=gemini_result
    )

    # ------------------------------
    # Return the results
    # ------------------------------
    return AllergyStandardizeOutput(corrections=verified_results)
