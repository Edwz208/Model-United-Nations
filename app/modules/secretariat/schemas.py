# app/modules/secretariat/schemas.py

from pydantic import BaseModel, ConfigDict
from typing import Optional

class ExecIn(BaseModel):
    name: str
    position: str

class ExecPatch(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None

class SecretariatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    secretariat_id: int
    name: str
    position: str
