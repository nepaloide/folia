from fastapi import APIRouter

from app.api.v1 import plants

router = APIRouter()

router.include_router(plants.router, prefix="/plants", tags=["plants"])
