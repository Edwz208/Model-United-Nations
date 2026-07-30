# app/modules/countries/schemas.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Annotated
from app.modules.countries.models import CountryRole

class CountryIn(BaseModel):
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
    delegate4: Optional[str] = None
    councils: Optional[list[int]] = None
    amendments_submitted: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    speaker_points: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    login: Annotated[Optional[str], Field(strict=True, min_length=4)] = None

class SelectCountriesToDelete(BaseModel):
    countries: list[int]

class ImportCountriesFromSpreadsheet(BaseModel):
    url: str

class UpdateSpeakerPoints(BaseModel):
    country: int
    speaker_points: int

class CountryListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    country_id: int
    name: str
    amendments_submitted: int
    speaker_points: int
    role: CountryRole
    councils: list[int]
    main_council: Optional[int] = None

class CountryProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    country_id: int
    name: str
    delegate1: Optional[str] = None
    delegate2: Optional[str] = None
    delegate3: Optional[str] = None
    delegate4: Optional[str] = None
    login: Optional[str] = None
    amendments_submitted: int
    speaker_points: int
    role: CountryRole
    councils: list[int]
    main_council: Optional[int] = None
