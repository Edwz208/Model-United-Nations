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
    amendments_submitted: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    speaker_points: Annotated[Optional[int], Field(strict=True, ge=0)] = None # is this allowed?
    login: Annotated[str, Field(strict=True, min_length=4)] # use pydantic types for domain rule not api rules, e.g for creating a type
    
class Resolution(BaseModel):
    title: str
    council_id: str
    clauses: Annotated[int, Field(strict=True, ge=0)]
    submitter: Annotated[int, Field(strict=True, ge=0)]
    seconder: Annotated[int, Field(strict=True, ge=0)]
    negator: Annotated[int, Field(strict=True, ge=0)]

class ResolutionPatch(BaseModel):
    title: Optional[str] = None
    council_id: Optional[str] = None 
    status: Optional[str] = None
    clauses: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    submitter: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    seconder: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    negator: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    url: Optional[str] = None

class Amendment(BaseModel):
    resolution_id: Annotated[int, Field(strict=True, ge=0)]
    status: Optional[str] = 'pending review'
    clause: Annotated[int, Field(strict=True, ge=0)]
    submitter: Annotated[int, Field(strict=True, ge=0)]
    content: str

class AmendmentPatch(BaseModel):
    resolution_id: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    status: Optional[str] = None
    clause: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    submitter: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    content: Optional[str] = None

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
