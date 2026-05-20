from fastapi import APIRouter

from app.api.v1 import plants
from app.modules.auth.router import router as auth_router

router = APIRouter()

router.include_router(plants.router, prefix="/plants", tags=["plants"])
router.include_router(auth_router, prefix="/auth")
