# app/modules/countries/router.py

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from app.core.dependencies import require_admin, require_member_or_admin
from app.core.database import get_db
from app.modules.countries.repository import CountryRepository
from app.modules.countries.service import CountryService
from app.modules.countries.schemas import CountryIn, CountryPatch, SelectCountriesToDelete, UpdateSpeakerPoints, ImportCountriesFromSpreadsheet, CountryListOut, CountryProfileOut

router = APIRouter(prefix="/countries", tags=["countries"])

def get_country_service(session: AsyncSession = Depends(get_db)) -> CountryService:
    return CountryService(CountryRepository(session))

@router.post("/import-from-sheet", status_code=status.HTTP_200_OK)
async def import_countries_from_sheet(spreadsheet_url: ImportCountriesFromSpreadsheet, current_user=Depends(require_admin), service: CountryService = Depends(get_country_service)) -> dict[str, Any]:
    await service.import_from_sheet(spreadsheet_url.url)
    return {"message": "success"}

@router.patch('/{country_id}', status_code=status.HTTP_200_OK)
async def update_country(country_id: int, country: CountryPatch, current_user=Depends(require_admin), service: CountryService = Depends(get_country_service)) -> dict[str, Any]:
    result = await service.update_country(country, country_id)
    return {"message": "success", "country": result}

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_country(country: CountryIn, service: CountryService = Depends(get_country_service)) -> dict[str, Any]:
    result = await service.add_country(country)
    return {"message": "success", "country": result}

@router.get("", status_code=status.HTTP_200_OK)
async def list_countries(current_user=Depends(require_member_or_admin), service: CountryService = Depends(get_country_service)) -> list[CountryListOut]:
    return await service.get_countries_general()

@router.get("/{country_id}", status_code=status.HTTP_200_OK)
async def get_country(country_id: int, current_user=Depends(require_member_or_admin), service: CountryService = Depends(get_country_service)) -> dict[str, Any]:
    result = await service.get_single_country(target_id=country_id, sender_id=current_user.get("id"), role=current_user.get("role"))
    return {"message": "success", "country": result}

@router.delete("", status_code=status.HTTP_200_OK)
async def delete_countries(countries_list: SelectCountriesToDelete, current_user=Depends(require_admin), service: CountryService = Depends(get_country_service)) -> dict[str, Any]:
    result = await service.delete_countries(countries_list.countries)
    return {"message": "success", "country": result}

@router.post("/speaker-points", status_code=status.HTTP_200_OK)
async def update_speaker_points(countryToUpdate: UpdateSpeakerPoints, current_user=Depends(require_admin), service: CountryService = Depends(get_country_service)) -> dict[str, Any]:
    result = await service.update_speaker_points(country=countryToUpdate.country, speaker_points=countryToUpdate.speaker_points)
    return {"message": "success", "country": result}
