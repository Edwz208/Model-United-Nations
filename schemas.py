from pydantic import BaseModel
from typing import Optional, List

class User(BaseModel):
    code: str
    country: str
    
class Country(BaseModel):
    assigned_country: str
    delegate1: str
    delegate2: Optional[str] = None
    delegate3: Optional[str] = None
    delegate4: Optional[str] = None
    role: str = "member"
    amendments_submitted: Optional[int] = 0
    speaker_points: Optional[int] = 0
    login: str
    id: int

class CountryPatch(BaseModel):
    assigned_country: Optional[str] = None
    delegate1: Optional[str] = None
    delegate2: Optional[str] = None
    delegate3: Optional[str] = None
    delegate4: Optional[str] = None
    role: Optional[str] = "member"
    amendments_submitted: Optional[int] = 0
    speaker_points: Optional[int] = 0
    login: Optional[str] = None
    id: int
    
class Resolution(BaseModel):
    title: str
    council: int
    status: str
    clauses: int
    submitter: str
    seconder: str
    negator: str

class ResolutionPatch(BaseModel):
    title: Optional[str] = None
    council: Optional[int] = None 
    status: Optional[str] = None
    clauses: Optional[int] = None
    submitter: Optional[str] = None
    seconder: Optional[str] = None
    negator: Optional[str] = None
    url: Optional[str] = None

class Amendment(BaseModel):
    resolution_title: str
    resolution_id: int
    status: Optional[str] = 'pending review'
    clause: int
    submitter: List[str] 
    content: str

class AmendmentPatch(BaseModel):
    resolution_title: Optional[str] = None
    resolution_id: Optional[int] = None
    status: Optional[str] = 'pending review'
    clause: Optional[int] = None
    submitter: Optional[List[str]] = None
    content: Optional[str] = None

class Exec(BaseModel):
    name: str
    position: str
    id: int

class ExecPatch(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    id: int