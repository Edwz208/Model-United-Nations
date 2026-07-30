# app/modules/resolution/schemas.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Annotated

class ResolutionCreateValidate(BaseModel):
    title: str
    council_id: Annotated[int, Field(strict=True, ge=0)]
    clauses: Annotated[int, Field(ge=0)]
    submitter: Annotated[int, Field(ge=0)]
    seconder: Annotated[int, Field(ge=0)]
    negator: Annotated[int, Field(ge=0)]
    number: Annotated[int, Field(ge=0)]

class ResolutionPatch(BaseModel):
    title: Optional[str] = None
    council_id: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    res_status: Optional[str] = None
    clauses: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    submitter: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    seconder: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    negator: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    number: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    url: Optional[str] = None

class SelectResolutionsToDelete(BaseModel):
    resolution_ids: list[int]

class ResolutionListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    resolution_id: int
    number: int
    title: str
    clauses: int
    council_id: int
    status: str
    amendment_count: int

class ResolutionDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    resolution_id: int
    number: int
    title: str
    clauses: int
    status: str
    council_id: int
    amendment_count: int
    submitter: Optional[int] = None
    seconder: Optional[int] = None
    negator: Optional[int] = None
