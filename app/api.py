from fastapi import APIRouter

from app.modules.authentication import endpoints as auth_endpoints
from app.modules.allergy_standardizer import endpoints as allergy_endpoints


router = APIRouter()
router.include_router(auth_endpoints.router, tags=["authentication"], prefix="/v1")
router.include_router(allergy_endpoints.router, tags=["standardizer"], prefix="/v1")
