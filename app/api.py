from fastapi import APIRouter

from app.modules.allergy_standardizer import endpoints

router = APIRouter()
router.include_router(endpoints.router, tags=["standardizer"], prefix="/v1")
