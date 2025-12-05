from pydantic import BaseModel, conint, constr
from typing import Optional

class User(BaseModel):
    code: constr(min_length=2)
    country: constr(min_length=2)
    
class Country(BaseModel):
    assigned_country: str
    delegate1: str
    delegate2: Optional[str] = None
    delegate3: Optional[str] = None
    delegate4: Optional[str] = None
    role: Optional[str] = 'member'
    amendments_submitted: Optional[conint(ge=0)] = 0
    speaker_points: Optional[conint(ge=0)] = 0
    login: constr(min_length=2)
    councils: list[int] 

class CountryPatch(BaseModel):
    assigned_country: Optional[str] = None
    delegate1: Optional[str] = None
    delegate2: Optional[str] = None
    delegate3: Optional[str] = None
    delegate4: Optional[str] = None # no role here
    amendments_submitted: Optional[conint(ge=0)] = None
    speaker_points: Optional[conint(ge=0)] = None # is this allowed?
    login: Optional[constr(min_length=2)] = None
    
class Resolution(BaseModel):
    title: str
    council_id: str
    clauses: conint(ge=0)
    submitter: conint(ge=0)
    seconder: conint(ge=0)
    negator: conint(ge=0)

class ResolutionPatch(BaseModel):
    title: Optional[str] = None
    council_id: Optional[str] = None 
    status: Optional[str] = None
    clauses: Optional[conint(ge=0)] = None
    submitter: Optional[conint(ge=0)] = None
    seconder: Optional[conint(ge=0)] = None
    negator: Optional[conint(ge=0)] = None
    url: Optional[str] = None

class Amendment(BaseModel):
    resolution_id: conint(ge=0)
    status: Optional[str] = 'pending review'
    clause: conint(ge=0)
    submitter: list[conint(ge=0)] 
    content: str

class AmendmentPatch(BaseModel):
    resolution_id: Optional[conint(ge=0)] = None
    status: Optional[str] = None
    clause: Optional[conint(ge=0)] = None
    submitter: Optional[list[conint(ge=0)]] = None
    content: Optional[str] = None

class Exec(BaseModel):
    name: str
    position: str

class ExecPatch(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None

class Council(BaseModel):
    name: str
    resolution_count: conint(ge=0)

class CouncilPatch(BaseModel):
    name: Optional[str] = None
    resolution_count: Optional[int] = None
