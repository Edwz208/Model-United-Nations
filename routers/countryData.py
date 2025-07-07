from fastapi import APIRouter, HTTPException, status, Depends
import csv
import requests
import io
import os
from schemas import Country
from schemas import Exec
from random import randrange
import time
from db import get_async_pool
from psycopg.rows import dict_row
from authentication import hash, get_current_user
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


pool = get_async_pool()
router = APIRouter()


def sanitizeKey(key):
    return key.strip().lower().replace("#", "").replace(" ", "_")


async def uniqueLogin():
    while True:
        randomNum = await hash(str(randrange(100000, 1000000)))
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(
                    """SELECT exists (SELECT 1 FROM delegates WHERE login = %s LIMIT 1);""",
                    (randomNum,),
                )
                unique = await cursor.fetchone()
                if unique:
                    return randomNum


@router.get("/sheet-export")
async def sheetExport(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = get_current_user(token)
    if payload.get("role").equals("member"):
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
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                for row in data:
                    del row["school"]
                    row["role"] = "member"
                    await cursor.execute(
                        """INSERT INTO delegates (country, delegate1, delegate2, delegate3, delegate4, login, role) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (country) DO UPDATE
                        SET delegate1 = EXCLUDED.delegate1,
                        delegate2 = EXCLUDED.delegate2,
                        delegate3 = EXCLUDED.delegate3,
                        delegate4 = EXCLUDED.delegate4,
                        login = CASE WHEN delegates.login IS NULL OR delegates.login = '' THEN EXCLUDED.login
                        ELSE delegates.login END,
                        role = EXCLUDED.role;""",
                        (
                            row["assigned_country"],
                            row["delegate_1"],
                            row["delegate_2"],
                            row["delegate_3"],
                            row["delegate_4"],
                            await uniqueLogin(),
                            "member",
                        ),
                    )
            return data
    else:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized page"
            )


@router.get("/get-countries", status_code = status.HTTP_200_OK)
async def getAll():
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute("""SELECT * from delegates""")
            allCount = await cursor.fetchall()
            return allCount


@router.get("/select-country/{country}")
async def selectCountry(country: str):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute("""SELECT * FROM delegates WHERE country=%s""", (country,))
            result = await cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Country with name {country} was not found",
                )
            return result


@router.delete("/select-country/{country}")
async def deleteCountry(country: str):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """DELETE FROM delegates WHERE country = %s RETURNING *""", (country,)
            )
            if not await cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Country with name {country} was not found",
                )
            return {"message": f"{country} deleted"}


@router.post('/single-country')
async def oneCountry(country: Country):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            country.login = await hash(country.login)
            await cursor.execute('''INSERT INTO delegates (country, delegate1, delegate2, delegate3, delegate4, role, login) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (country)
                           DO UPDATE SET delegate1 = EXCLUDED.delegate1, delegate2 = EXCLUDED.delegate2, delegate3 = EXCLUDED.delegate3, delegate4 = EXCLUDED.delegate4, role = EXCLUDED.role, login = EXCLUDED.login RETURNING *;''',
                           (country.assigned_country, country.delegate1,country.delegate2,country.delegate3,country.delegate4,country.role,country.login))
            return await cursor.fetchone()

@router.post("/set-exec", status_code = status.HTTP_200_OK)
async def setExec(person: Exec):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute('''INSERT INTO secretariat (name, position) VALUES (%s,%s) ON CONFLICT (name)
                           DO UPDATE SET name = EXCLUDED.name, position = EXCLUDED.position RETURNING *;''',
                           (person.name, person.position))
            return await cursor.fetchone()
        
@router.get("/get-secretariat", status_code = status.HTTP_200_OK)
async def getAll():
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute("""SELECT * from secretariat""")
            allCount = await cursor.fetchall()
            return allCount
        
