# app/modules/amendments/schemas.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Annotated
from datetime import datetime

class AmendmentIn(BaseModel):
    resolution_id: Annotated[int, Field(strict=True, ge=0)]
    status: Annotated[str, Field(max_length=50)] = 'pending review'
    clause: Annotated[int, Field(strict=True, ge=0)]
    submitter: Annotated[int, Field(strict=True, ge=0)]
    content: Annotated[str, Field(max_length=500)]

class AmendmentPatch(BaseModel):
    resolution_id: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    status: Annotated[Optional[str], Field(max_length=50)] = None
    clause: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    submitter: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    content: Annotated[Optional[str], Field(max_length=500)] = None

class ApproveRejectAmendment(BaseModel):
    status: str
    reject_message: Annotated[Optional[str], Field(max_length=100)] = None

class AmendmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    amendment_id: int
    content: Optional[str] = None
    clause_number: int
    resolution_id: int
    submitter: int
    status: str
    modified_at: datetime
