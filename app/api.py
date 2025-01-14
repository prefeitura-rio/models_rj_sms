from fastapi import APIRouter

from app.modules.authentication import endpoints as auth_endpoints
from app.modules.allergy_standardizer import endpoints as allergy_endpoints
from app.modules.medlm import endpoints as medlm_endpoints


router = APIRouter()
router.include_router(auth_endpoints.router, tags=["Authentication"], prefix="/v1")
router.include_router(medlm_endpoints.router, tags=["Core"], prefix="/v1")
router.include_router(allergy_endpoints.router, tags=["Use Cases"], prefix="/v1")
