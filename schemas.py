from pydantic import BaseModel
from typing import Optional

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
    # councils: Optional[str] = None
    login: str
    
class Resolution(BaseModel):
    title: str
    number: int
    council: int
    status: str
    clauses: int
    submitter: str
    seconder: str
    negator: str

class Exec(BaseModel):
    name: str
    position: str
