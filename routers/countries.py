from fastapi import APIRouter, status, Depends
from schemas import Country, CountryPatch, SelectCountriesToDelete, UpdateSpeakerPoints
from auth.dependencies import require_admin, require_member_or_admin
from typing import Any
from services.countries import update_speaker_points_service, get_countries_general_service, get_single_country_service, delete_country_service, update_country_service, sheet_export_service, add_country_service

router = APIRouter()
@router.get("/sheet-export",status_code = status.HTTP_200_OK)
async def sheet_xport(current_user = Depends(require_admin)) -> dict[str, Any]:
    await sheet_export_service()
    return {"message": "success"} # dont resend data

@router.patch('/update-single-country/{country_id}',status_code = status.HTTP_200_OK)
async def update_country(country_id: int, country: CountryPatch, current_user=Depends(require_admin)) -> dict[str, Any]:
    result = await update_country_service(country, country_id)
    return {"message": "success", "country": result}

@router.post('/add-single-country', status_code=status.HTTP_200_OK)
async def add_one_country(country: Country, current_user=Depends(require_admin)):
    result = await add_country_service(country)
    return {"message": "success", "country": result}

@router.get("/get-countries", status_code = status.HTTP_200_OK)
async def get_all_countries(current_user=Depends(require_member_or_admin)) -> list[dict[str, Any]]:
    all_countries = await get_countries_general_service()
    return all_countries
 
# @router.get('/countries-council/{council_id}', status_code = status.HTTP_200_OK)
# async def get_countries_in_council(council_id: int, current_user=Depends(require_member_or_admin)) -> list[dict[str, Any]]:
#     countries_in_council = await get_countries_in_council_service(council_id)
#     return countries_in_council

@router.get("/select-country/{country_id}",status_code = status.HTTP_200_OK)
async def select_country(country_id: int, current_user=Depends(require_member_or_admin)) -> dict[str, Any]:
    result = await get_single_country_service(target_id=country_id, sender_id=current_user.get("id"), role=current_user.get("role"))
    return {"message": "success", "country": result}

@router.delete("/select-country", status_code = status.HTTP_200_OK)
async def delete_country(countries_list: SelectCountriesToDelete, current_user=Depends(require_admin)) -> dict[str, Any]:
    result = await delete_country_service(countries_list.countries)
    return {"message": "success", "country": result}

@router.post("/update-speaker-points", status_code = status.HTTP_200_OK)
async def update_speaker_points(countryToUpdate: UpdateSpeakerPoints, current_user=Depends(require_admin)) -> dict[str, Any]:
    result = await update_speaker_points_service(country=countryToUpdate.country, speaker_points=countryToUpdate.speaker_points)
    return {"message": "success", "country": result}