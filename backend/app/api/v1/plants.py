from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.modules.auth.schemas import UserResponse
from app.schemas.plant import PlantResponse

router = APIRouter()


@router.get("/", response_model=list[PlantResponse])
async def list_plants(user: UserResponse = Depends(get_current_user)):
    """List all plants for the authenticated user (placeholder)."""
    _ = user.id  # used when real plant filtering is implemented
    return []


@router.get("/{plant_id}", response_model=PlantResponse)
async def get_plant(
    plant_id: int,
    user: UserResponse = Depends(get_current_user),
):
    """Get a single plant by ID (placeholder)."""
    _ = user.id  # used when real plant retrieval is implemented
    # TODO: implement when models and services exist
    raise NotImplementedError("Plant retrieval not yet implemented")
