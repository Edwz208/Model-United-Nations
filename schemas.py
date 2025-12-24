from pydantic import BaseModel, Field
from typing import Optional, Annotated

class User(BaseModel):
    code: Annotated[str, Field(strict=True, min_length=4)]
    country: Annotated[str, Field(strict=True, min_length=4)]
    
class Country(BaseModel):
    assigned_country: str
    delegate1: str
    delegate2: Optional[str] = None
    delegate3: Optional[str] = None
    delegate4: Optional[str] = None
    role: Optional[str] = 'member'
    amendments_submitted: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    speaker_points: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    login: Annotated[str, Field(strict=True, min_length=2)]
    councils: list[int] 

class CountryPatch(BaseModel):
    assigned_country: Optional[str] = None
    delegate1: Optional[str] = None
    delegate2: Optional[str] = None
    delegate3: Optional[str] = None
    delegate4: Optional[str] = None # no role here
    councils: Optional[list[int]] = None
    amendments_submitted: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    speaker_points: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    login: Annotated[Optional[str], Field(strict=True, min_length=4)] = None # use pydantic types for domain rule not api rules, e.g for creating a type
    
class Resolution(BaseModel):
    title: str
    council_id: Annotated[int, Field(strict=True, ge=0)]
    clauses: Annotated[int, Field(ge=0)]
    submitter: Annotated[int, Field(ge=0)]
    seconder: Annotated[int, Field(ge=0)]
    negator: Annotated[int, Field(ge=0)]

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

class Amendment(BaseModel):
    resolution_id: Annotated[int, Field(strict=True, ge=0)]
    status: Annotated[str, Field(max_length=50)] = 'pending review' #must be string, remove optional
    clause: Annotated[int, Field(strict=True, ge=0)]
    submitter: Annotated[int, Field(strict=True, ge=0)]
    content: Annotated[str, Field(max_length=500)]

class AmendmentPatch(BaseModel):
    resolution_id: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    status: Annotated[Optional[str], Field(max_length=50)] = None
    clause: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    submitter: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    content: Annotated[Optional[str], Field(max_length=500)] = None
    
class Exec(BaseModel):
    name: str
    position: str

class ExecPatch(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None

class Council(BaseModel):
    name: str
    resolution_count: Annotated[int, Field(strict=True, ge=0)]

class CouncilPatch(BaseModel):
    name: Optional[str] = None
    resolution_count: Optional[int] = None

class Projection(BaseModel):
    active_screen: Optional[str] = None
    temporary_speaker_1: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    temporary_speaker_2: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    temporary_speaker_3: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    paging_system: Optional[bool] = None
    message: Annotated[Optional[str], Field(max_length=600)] = None
    vote_to_open_resolution_number: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    vote_pass_fail_or_cancel: Optional[str] = None
    clear_Vote: Optional[bool] = None

class ApproveRejectAmendment(BaseModel):
    status: str
    reject_message: Annotated[Optional[str], Field(max_length=100)] = None