from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class PlantBase(BaseModel):
    name: str
    species: Optional[str] = None
    notes: Optional[str] = None


class PlantCreate(PlantBase):
    pass


class PlantUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    notes: Optional[str] = None


class PlantResponse(PlantBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: str
    created_at: datetime
    updated_at: datetime
