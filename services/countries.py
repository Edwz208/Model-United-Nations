
from typing import Any
from db.utils import get_cursor, fetch_all, fetch_one, transaction, execute
from fastapi import HTTPException, status
from random import randrange
from schemas import CountryPatch, Country
from config import settings
from utils.utils import sanitize_key
import requests
import csv
import io

async def get_countries_general_service() -> list[dict[str, Any]]:
    return await fetch_all(
        '''
        WITH main AS (
            SELECT council_id AS main_council
            FROM councils
            WHERE is_main = true
            LIMIT 1
        )
        SELECT
            c.name,
            c.amendments_submitted,
            c.speaker_points,
            c.country_id,
            c.role,
            ARRAY(
                SELECT DISTINCT v
                FROM unnest(
                    COALESCE(
                        array_agg(DISTINCT cc.council_id) FILTER (WHERE cc.council_id IS NOT NULL),
                        '{}'::int[]
                    ) || ARRAY[main.main_council]
                ) AS v
                ORDER BY v
            ) AS councils,
            main.main_council
        FROM countries c
        CROSS JOIN main
        LEFT JOIN country_council cc ON cc.country_id = c.country_id
        WHERE c.role = %s
        GROUP BY
            c.name, c.amendments_submitted, c.speaker_points, c.country_id, c.role, main.main_council
        ORDER BY LOWER(c.name) ASC
        ''',
        ('member',)
    )

# async def get_countries_in_council_service(council_id: int) -> list[dict[str, Any]]:
#     countriesInCouncil = await fetch_all('''SELECT c.name, c.amendments_submitted, c.speaker_points, c.country_id FROM countries AS c JOIN country_council AS cc ON c.country_id = cc.country_id WHERE cc.council_id = %s AND c.role = %s ORDER BY c.name ASC ''', (council_id, 'member'))
#     return countriesInCouncil
        
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
            COALESCE(
                array_remove(array_agg(DISTINCT cc.council_id), NULL),
                '{}'::int[]
            ) AS councils,
            MAX(CASE WHEN co.is_main THEN co.council_id END) AS main_council
        FROM countries c
        LEFT JOIN country_council cc ON cc.country_id = c.country_id
        LEFT JOIN councils co ON co.council_id = cc.council_id
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
        print(target_id)
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
    
    query = '''
WITH new_country AS (
  INSERT INTO countries (
    name, delegate1, delegate2, delegate3, delegate4,
    role, login, amendments_submitted, speaker_points
  )
  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
  RETURNING
    name, delegate1, delegate2, delegate3, delegate4,
    role, login, amendments_submitted, speaker_points, country_id
),
links AS (
  INSERT INTO country_council (country_id, council_id)
  SELECT new_country.country_id, cid
  FROM new_country
  CROSS JOIN unnest(COALESCE(%s::int[], ARRAY[]::int[])) AS cid
  ON CONFLICT DO NOTHING
)
SELECT * FROM new_country;'''


    params = (
        country.assigned_country,
        country.delegate1,
        country.delegate2,
        country.delegate3,
        country.delegate4,
        country.role,
        country.login,
        country.amendments_submitted or 0,
        country.speaker_points or 0,
        country.councils,
    )
    result = await fetch_one(query, params)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country could not be created",
    )
    return result

async def update_country_service(country: CountryPatch, country_id: int) -> dict[str, Any]:
    print(country)
    update_query = '''
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
    RETURNING
      name, delegate1, delegate2, delegate3, delegate4,
      login, amendments_submitted, speaker_points, country_id;
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
        result = await fetch_one(update_query, params, cursor=cursor)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found",
            )

        await execute(
            '''DELETE FROM country_council WHERE country_id = %s AND council_id NOT IN (SELECT council_id FROM councils WHERE is_main = TRUE);''',
            (country_id,),
            cursor=cursor,
        )

        await execute(
            '''
            INSERT INTO country_council (country_id, council_id)
            SELECT %s, cid
            FROM unnest(%s::int[]) AS cid
            ON CONFLICT DO NOTHING;
            ''',
            (country_id, country.councils),
            cursor=cursor,
        )

        return result

async def delete_country_service(ids: list[int]) -> list[dict[str, Any]]:
    result = await fetch_all('''DELETE FROM countries WHERE role != 'admin' AND country_id = ANY(%s) RETURNING name, delegate1, delegate2, delegate3, delegate4, login, amendments_submitted, speaker_points, country_id''', (ids,))
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

async def sheet_export_service(url) -> None: # need async? 
    try:
        response = requests.get(url)
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid url")

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
            country = row.get("assigned_country", "").strip()
            if not country and not any((v or "").strip() for v in row.values()):
                continue
            if country.lower() == "schools":
                break
            row.pop("school", None)
            row["role"] = 'member'
            await execute(
                '''INSERT INTO countries (name, delegate1, delegate2, delegate3, delegate4, login, speaker_points, role) VALUES (%s,%s,%s,%s,%s,%s,%s, %s) ON CONFLICT (name) DO UPDATE
                SET delegate1 = EXCLUDED.delegate1,
                delegate2 = EXCLUDED.delegate2,
                delegate3 = EXCLUDED.delegate3,
                delegate4 = EXCLUDED.delegate4,
                login = CASE WHEN countries.login IS NULL OR countries.login = '' THEN EXCLUDED.login
                ELSE countries.login END,
                speaker_points = EXCLUDED.speaker_points,
                role = EXCLUDED.role;''',
                (
                    row.get("assigned_country"),
                    row.get("delegate_1"),
                    row.get("delegate_2"),
                    row.get("delegate_3"),
                    row.get("delegate_4"),
                    await unique_login_service(),
                    0,
                    row.get("role"),
                ), cursor=cursor
            )

async def update_speaker_points_service(country: int, speaker_points: int) -> dict[str, Any]:
    result = await fetch_one('''UPDATE countries SET speaker_points = speaker_points + %s WHERE country_id = %s RETURNING *''',(speaker_points, country,))
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country not found")
    return result