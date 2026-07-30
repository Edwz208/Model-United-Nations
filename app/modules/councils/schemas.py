# app/modules/councils/schemas.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Annotated

class CouncilIn(BaseModel):
    name: str
    resolution_count: Annotated[int, Field(strict=True, ge=0)]

class CouncilPatch(BaseModel):
    name: Optional[str] = None
    resolution_count: Optional[int] = None

class CouncilOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    council_id: int
    name: str
    resolution_count: int
    is_main: bool
