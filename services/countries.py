
from typing import Any
from db.utils import get_cursor, fetch_all, fetch_one, transaction, execute
from fastapi import HTTPException, status
from random import randrange
from schemas import CountryPatch, Country
from config import settings
from backend.utils.utils import sanitize_key
import requests
import csv
import io

async def get_countries_general_service() -> list[dict[str, Any]]:
    allCountries = await fetch_all('''SELECT name, amendments_submitted, speaker_points, country_id from countries WHERE role = %s ORDER BY name ASC''', ('member',))
    return allCountries

async def get_countries_in_council_service(council_id: int) -> list[dict[str, Any]]:
    countriesInCouncil = await fetch_all('''SELECT c.name, c.amendments_submitted, c.speaker_points, c.country_id FROM countries AS c JOIN country_council AS cc ON c.country_id = cc.country_id WHERE cc.council_id = %s AND c.role = %s ORDER BY c.name ASC ''', (council_id, 'member'))
    return countriesInCouncil
        
async def personal_profile_service(id: int) -> dict[str, Any]:
    country = await fetch_one(
        '''
        SELECT
            c.name,
            c.delegate1,
            c.delegate2,
            c.delegate3,
            c.delegate4,
            c.login,
            c.amendments_submitted,
            c.speaker_points,
            c.country_id,
            c.role,
            array_agg(cc.council_id) AS councils,
            MAX(
                CASE
                    WHEN co.is_main THEN co.council_id
                    ELSE NULL
                END
            ) AS main_council
        FROM countries c
        JOIN country_council cc ON cc.country_id = c.country_id
        JOIN councils co ON co.council_id = cc.council_id
        WHERE c.country_id = %s
        GROUP BY
            c.name, c.delegate1, c.delegate2, c.delegate3,
            c.delegate4, c.login, c.amendments_submitted,
            c.speaker_points, c.country_id, c.role
        ''',
        (id,)
    )

    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with id {id} does not exist."
        )

    return country

async def specific_profile_service(id: int) -> dict[str, Any]:
    country = await fetch_one(
        '''
        SELECT
            c.name,
            c.delegate1,
            c.delegate2,
            c.delegate3,
            c.delegate4,
            c.amendments_submitted,
            c.speaker_points,
            c.country_id,
            c.role,
            array_agg(cc.council_id) AS councils,
            MAX(
                CASE
                    WHEN co.is_main THEN co.council_id
                    ELSE NULL
                END
            ) AS main_council
        FROM countries c
        JOIN country_council cc ON cc.country_id = c.country_id
        JOIN councils co ON co.council_id = cc.council_id
        WHERE c.country_id = %s
        GROUP BY
            c.name, c.delegate1, c.delegate2, c.delegate3,
            c.delegate4, c.login, c.amendments_submitted,
            c.speaker_points, c.country_id, c.role
        ''',
        (id,)
    )

    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with id {id} does not exist."
        )

    return country

async def get_single_country_service(target_id: int, sender_id: int, role: str) -> dict[str, Any]: 
    if sender_id == target_id or 'admin' == role:
        result = await personal_profile_service(target_id)
    else:
        result = await specific_profile_service(target_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with id {target_id} was not found",
    )
    return result

async def add_country_service(country: Country) -> dict[str, Any]:
    result = await fetch_one("""WITH new_country AS (INSERT INTO countries (name, delegate1, delegate2, delegate3, delegate4, role, login, amendments_submitted, speaker_points) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING country_id) INSERT INTO country_council (country_id, council_id) SELECT new_country.country_id, cid FROM new_country, unnest(%s::int[]) as cid ON CONFLICT DO NOTHING RETURNING name, delegate1, delegate2, delegate3, delegate4, role, login, amendments_submitted, speaker_point, country_id""", (country.assigned_country, country.delegate1, country.delegate2, country.delegate3, country.delegate4, country.role, country.login, country.amendments_submitted, country.speaker_points, country.councils))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country could not be created",
    )
    return result

async def update_country_service(country: CountryPatch, country_id: int) -> dict[str, Any]:
    query = '''
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
        RETURNING name, delegate1, delegate2, delegate3, delegate4, login, amendments_submitted, speaker_points, country_id;
        '''
    params = (
        country.assigned_country,
        country.delegate1,
        country.delegate2,
        country.delegate3,
        country.delegate4,
        country.login,
        country.amendments_submitted,
        country.speaker_points,
        country_id,
    )
    async with transaction() as cursor:
        result = await fetch_one(query, params, cursor=cursor)
        if not result: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country not found")
        await execute('''WITH delete_prev AS (DELETE FROM country_council WHERE country_id = %s AND council_id NOT IN (SELECT council_id FROM councils WHERE is_main = TRUE)) INSERT INTO country_council (country_id, council_id) SELECT %s, unnest(%s::int[])''',(country_id, country_id, country.councils,),cursor=cursor)
        return result

async def delete_country_service(id: int) -> dict[str, Any]:

    result = await fetch_one('''DELETE FROM countries WHERE country_id = %s AND role != 'admin' RETURNING name, delegate1, delegate2, delegate3, delegate4, login, amendments_submitted, speaker_points, country_id''', (id,))
    # cascades to country_council
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country not found")
    return result

async def unique_login_service() -> str:
    async with get_cursor() as cursor:
        while True:
            random_num = str(randrange(100000, 1000000)) #unhashed for now
            result = await fetch_one('''SELECT exists (SELECT 1 FROM countries WHERE login = %s LIMIT 1);''', (random_num,), cursor=cursor) or {}
            if not result.get("exists"):
                return random_num 

async def sheet_export_service() -> None: # need async? 
    url = settings.SPREADSHEET
    response = requests.get(url)
    csv_string = response.text
    f = io.StringIO(csv_string)
    first_line = next(f)
    raw_keys = first_line.strip().split(",")
    sanitized_keys = [sanitize_key(name) for name in raw_keys]
    reader = csv.DictReader(f, fieldnames=sanitized_keys)
    data = list(reader)
    print(data)
    async with transaction() as cursor:
        for row in data:
            row.pop("school", None)
            row["role"] = 'member'
            await execute(
                '''INSERT INTO countries (name, delegate1, delegate2, delegate3, delegate4, login, role) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (name) DO UPDATE
                SET delegate1 = EXCLUDED.delegate1,
                delegate2 = EXCLUDED.delegate2,
                delegate3 = EXCLUDED.delegate3,
                delegate4 = EXCLUDED.delegate4,
                login = CASE WHEN countries.login IS NULL OR countries.login = '' THEN EXCLUDED.login
                ELSE countries.login END,
                role = EXCLUDED.role;''',
                (
                    row.get("assigned_country"),
                    row.get("delegate_1"),
                    row.get("delegate_2"),
                    row.get("delegate_3"),
                    row.get("delegate_4"),
                    await unique_login_service(),
                    row.get("role"),
                ), cursor=cursor
            )
        