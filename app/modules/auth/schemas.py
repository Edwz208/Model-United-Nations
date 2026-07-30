# app/modules/auth/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Annotated

class LoginIn(BaseModel):
    code: Annotated[str, Field(strict=True, min_length=4)]
    country: Annotated[str, Field(strict=True, min_length=4)]

class LoginOut(BaseModel):
    name: str
    country_id: int
    role: str
    accessToken: str

class RefreshOut(BaseModel):
    message: str
    accessToken: str
    role: Optional[str] = None
    name: Optional[str] = None
    country_id: Optional[int] = None
