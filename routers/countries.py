from fastapi import APIRouter, status, Depends
from schemas import Country, CountryPatch
from auth.dependencies import require_admin, require_member_or_admin
from typing import Any
from services.countries import get_countries_general_service, get_countries_in_council_service, get_single_country_service, delete_country_service, update_country_service, sheet_export_service

router = APIRouter()
@router.get("/sheet-export",status_code = status.HTTP_200_OK)
async def sheet_xport(current_user = Depends(require_admin)) -> dict[str, Any]:
    await sheet_export_service()
    return {"message": "success"} # dont resend data

@router.patch('/update-single-country',status_code = status.HTTP_200_OK)
async def update_country(country: CountryPatch, current_user=Depends(require_admin)) -> dict[str, Any]:
    result = await update_country_service(country)
    return {"message": "success", **result}

@router.post('/add-single-country', status_code=status.HTTP_200_OK)
async def add_one_country(country: Country, current_user=Depends(require_admin), council_ids: list[int] = []):
    result = await fetch_one("""WITH new_country AS (INSERT INTO countries (name, delegate1, delegate2, delegate3, delegate4, role, login, amendments_submitted, speaker_points) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING country_id) INSERT INTO country_council (country_id, council_id) SELECT new_country.country_id, cid FROM new_country, unnest(%s::int[]) as cid ON CONFLICT DO NOTHING RETURNING name, delegate1, delegate2, delegate3, delegate4, role, login, amendments_submitted, speaker_point, country_id""", (country.assigned_country, country.delegate1, country.delegate2, country.delegate3, country.delegate4, country.role, country.login, country.amendments_submitted, country.speaker_points), cursor=cursor)
    return result

@router.get("/get-countries", status_code = status.HTTP_200_OK)
async def get_all_countries(current_user=Depends(require_member_or_admin)) -> list[dict[str, Any]]:
    all_countries = await get_countries_general_service()
    return all_countries

@router.get('/countries-council', status_code = status.HTTP_200_OK)
async def get_countries_in_council(council_id: int, current_user=Depends(require_member_or_admin)) -> list[dict[str, Any]]:
    countries_in_council = await get_countries_in_council_service(council_id)
    return countries_in_council

@router.patch("/update-country-councils", status_code=status.HTTP_200_OK)
async def updateCountryCouncils(country_id: int, council_ids: list[int], current_user=Depends(require_admin)):
    async with transaction() as cursor:
        if council_ids:
            await execute('''DELETE FROM country_council WHERE country_id = %s AND council_id NOT IN %s AND council_id NOT IN (SELECT council_id FROM councils WHERE is_main = TRUE)''', (country_id, tuple(council_ids)), cursor=cursor)
        else:
            await execute('''DELETE FROM country_council WHERE country_id = %s AND council_id NOT IN (SELECT council_id FROM councils WHERE is_main = TRUE)''', (country_id, tuple(council_ids)), cursor=cursor)
        await execute('''INSERT INTO country_council (country_id, council_id) SELECT %s, cid FROM unnest(%s::int[]) as cid ON CONFLICT DO NOTHING''', (country_id, tuple(council_ids)), cursor=cursor)
    return {"message": "success"}

@router.get("/select-country/{country_id}",status_code = status.HTTP_200_OK)
async def select_country(country_id: int, current_user=Depends(require_member_or_admin)) -> dict[str, Any]:
    result = await get_single_country_service(target_id=country_id, sender_id=current_user.get("id"), role=current_user.get("role"))
    return {"message": "success", **result}

@router.delete("/select-country/{country_id}", status_code = status.HTTP_200_OK)
async def delete_country(country_id: int, current_user=Depends(require_admin)) -> dict[str, Any]:
    result = await delete_country_service(country_id)
    return {"message": "success", **result}
