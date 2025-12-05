from fastapi import APIRouter, HTTPException, status, Depends
import csv
import requests
import io
import os
from schemas import Country, CountryPatch
from random import randrange
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from helpers import require_admin, require_member_or_admin, fetch_all, fetch_one, execute, get_cursor, transaction

router = APIRouter()


def sanitizeKey(key: str) -> str:
    return key.strip().lower().replace("#", "").replace(" ", "_")

async def getCountriesGeneral() -> list[dict]:
    allCountries = await fetch_all("""SELECT name, amendments_submitted, speaker_points, country_id from countries WHERE role = %s ORDER BY country ASC""", ('member',))
    return allCountries

async def getCountriesPerCouncil(council_id: int) -> list[dict]:
    countriesInCouncil = await fetch_all("""SELECT c.name, c.amendments_submitted, c.speaker_points, c.country_id FROM countries c JOIN country_council cc ON c.country_id = cc.country_id WHERE cc.council_id = %s AND c.role = %s ORDER BY c.name ASC """, (council_id, 'member'))
    return countriesInCouncil
        
async def personalProfile(id: int) -> dict:
        personalCountry = await fetch_one("""SELECT name, delegate1, delegate2, delegate3, delegate4, login, amendments_submitted, speaker_points, country_id, role from countries WHERE country_id = %s""", (id,))
        if not personalCountry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country with id {id} does not exist.")
        return personalCountry

async def specificProfile(id: int) -> dict:
    specificCountry = await fetch_one("""SELECT name, delegate1, delegate2, delegate3, delegate4, amendments_submitted, speaker_points, country_id from countries WHERE country_id = %s""", (id,))
    if not specificCountry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country with id {id} does not exist.")
    return specificCountry
        
async def uniqueLogin() -> str:
    async with get_cursor() as cursor:
        while True:
            randomNum = str(randrange(100000, 1000000)) #unhashed for now
            result = await fetch_one("""SELECT exists (SELECT 1 FROM countries WHERE login = %s LIMIT 1);""", (randomNum,), cursor=cursor)
            if not result["exists"]:
                return randomNum 

@router.get("/sheet-export",status_code = status.HTTP_200_OK)
async def sheetExport(current_user = Depends(require_admin)):
    url = os.getenv("SPREADSHEET")
    response = requests.get(url)
    csvString = response.text
    f = io.StringIO(csvString)
    firstLine = next(f)
    rawKeys = firstLine.strip().split(",")
    sanitizedKeys = [sanitizeKey(name) for name in rawKeys]
    reader = csv.DictReader(f, fieldnames=sanitizedKeys)
    data = list(reader)
    print(data)
    for row in data:
        del row["school"]
        row["role"] = 'member'
        await execute(
            """INSERT INTO countries (name, delegate1, delegate2, delegate3, delegate4, login, role) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (name) DO UPDATE
            SET delegate1 = EXCLUDED.delegate1,
            delegate2 = EXCLUDED.delegate2,
            delegate3 = EXCLUDED.delegate3,
            delegate4 = EXCLUDED.delegate4,
            login = CASE WHEN countries.login IS NULL OR countries.login = '' THEN EXCLUDED.login
            ELSE countries.login END,
            role = EXCLUDED.role;""",
            (
                row["assigned_country"],
                row["delegate_1"],
                row["delegate_2"],
                row["delegate_3"],
                row["delegate_4"],
                await uniqueLogin(),
                row["role"],
            )
        )
        return data

# update single country
@router.patch('/update-single-country',status_code = status.HTTP_200_OK)
async def updateOneCountry(country: CountryPatch, current_user=Depends(require_member_or_admin)):
    if country.get('role') != 'admin':
        country = country.model_dump(exclude_unset=True)
        query = """
            UPDATE countries
            SET
            name = COALESCE(%s, name),
            delegate1 = COALESCE(%s, delegate1),
            delegate2 = COALESCE(%s, delegate2),
            delegate3 = COALESCE(%s, delegate3),
            delegate4 = COALESCE(%s, delegate4),
            login = COALESCE(%s, login),
            amendments_submitted = COALESCE(%s, amendments_submitted),
            speaker_points = COALESCE(%s, speaker_points)
            WHERE country_id = %s
            RETURNING *;
            """
        params = (
            country.get("assigned_country"),
            country.get("delegate1"),
            country.get("delegate2"),
            country.get("delegate3"),
            country.get("delegate4"),
            country.get("login"),
            country.get("amendments_submitted"),
            country.get("speaker_points"),
            country.get("id"),
        )
        result = await fetch_one(query, params)
        print(result)
    return result

@router.post('/add-single-country', status_code=status.HTTP_200_OK)
async def addOneCountry(country: Country, current_user=Depends(require_admin), council_ids: list[int] = []):
    async with transaction() as cursor:
        result = await fetch_one("""INSERT INTO countries (name, delegate1, delegate2, delegate3, delegate4, role, login, amendments_submitted, speaker_points) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING country_id, name;""", (country.assigned_country, country.delegate1, country.delegate2, country.delegate3, country.delegate4, country.role, country.login, country.amendments_submitted, country.speaker_points), cursor=cursor)
        country_id = result["country_id"]
        for council_id in council_ids:
            await execute("""INSERT INTO country_council (country_id, council_id) VALUES (%s, %s) ON CONFLICT (country_id, council_id) DO NOTHING;""", (country_id, council_id), cursor=cursor)
        return result

@router.get("/get-countries", status_code = status.HTTP_200_OK)
async def getAllCountries(current_user=Depends(require_member_or_admin)):
    allCountries = await getCountriesGeneral()
    print(allCountries)
    return allCountries

@router.get('/countries-council', status_code = status.HTTP_200_OK)
async def getCountriesInCouncil(council_id: int, current_user=Depends(require_member_or_admin)):
    countriesInCouncil = await getCountriesPerCouncil(council_id)
    return countriesInCouncil


@router.patch("/update-country-councils", status_code=status.HTTP_200_OK)
async def updateCountryCouncils(country_id: int, council_ids: list[int], current_user=Depends(require_admin)):
    async with transaction() as cursor:
        await execute("DELETE FROM country_council WHERE country_id = %s AND council_id NOT IN %s", (country_id, tuple(council_ids)), cursor=cursor)
        for cid in council_ids:
            await execute("INSERT INTO country_council (country_id, council_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (country_id, cid), cursor=cursor)
    return {"status": "success"}


@router.get("/select-country/{id}",status_code = status.HTTP_200_OK)
async def selectCountry(id: int, current_user=Depends(require_member_or_admin)):
    if id == current_user.get("id") or 'admin' == current_user.get("role"):
        result = await personalProfile(id)
    else:
        result = await specificProfile(id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with id {id} was not found",
        )
    return result

# delete
@router.delete("/select-country/{id}", status_code = status.HTTP_200_OK)
async def deleteCountry(id: str, current_user=Depends(require_admin)):
    result = await fetch_one("""DELETE FROM countries WHERE country_id = %s AND role != 'admin' RETURNING *""", (id,))
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country not found")
    return {"message": f"{result['country']} deleted"}
