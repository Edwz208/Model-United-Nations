from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    code: str
    country: str
    
class Country(BaseModel): #country creation
    assigned_country: str
    delegate1: str
    delegate2: Optional[str] = None
    delegate3: Optional[str] = None
    delegate4: Optional[str] = None
    role: str = 'member'
    amendments_submitted: Optional[int] = 0
    speaker_points: Optional[int] = 0
    login: str

class CountryPatch(BaseModel):
    assigned_country: Optional[str] = None
    delegate1: Optional[str] = None
    delegate2: Optional[str] = None
    delegate3: Optional[str] = None
    delegate4: Optional[str] = None # no role here
    amendments_submitted: Optional[int] = None
    speaker_points: Optional[int] = None # is this allowed?
    login: Optional[str] = None
    
class Resolution(BaseModel):
    title: str
    council_id: str
    clauses: int
    submitter: int
    seconder: int
    negator: int

class ResolutionPatch(BaseModel):
    title: Optional[str] = None
    council_id: Optional[str] = None 
    status: Optional[str] = None
    clauses: Optional[int] = None
    submitter: Optional[int] = None
    seconder: Optional[int] = None
    negator: Optional[int] = None
    url: Optional[str] = None

class Amendment(BaseModel):
    resolution_title: str
    resolution_id: int
    status: Optional[str] = 'pending review'
    clause: int
    submitter: list[int] 
    content: str

class AmendmentPatch(BaseModel):
    resolution_title: Optional[str] = None
    resolution_id: Optional[int] = None
    status: Optional[str] = None
    clause: Optional[int] = None
    submitter: Optional[list[int]] = None
    content: Optional[str] = None

class Exec(BaseModel):
    name: str
    position: str
    id: int

class ExecPatch(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    id: int
