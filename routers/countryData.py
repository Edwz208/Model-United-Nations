from fastapi import APIRouter, HTTPException, status, Depends
import csv
import requests
import io
import os
from schemas import Country, CountryPatch, Exec, ExecPatch
from random import randrange
from db import get_async_pool
from psycopg.rows import dict_row
from authentication import hash, get_current_user, roleList, verify
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from psycopg.errors import UniqueViolation

pool = get_async_pool()
router = APIRouter()


def sanitizeKey(key):
    return key.strip().lower().replace("#", "").replace(" ", "_")

async def getCountriesGeneral():
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute("""SELECT country, amendments_submitted, speaker_points from delegates WHERE role = %s""", (str(roleList.get("member")),))
            allCount = await cursor.fetchall()
            return allCount  
        
async def personalProfile(country: int):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute("""SELECT country, delegate1, delegate2, delegate3, delegate4, login, amendments_submitted, speaker_points from delegates WHERE id = %s""", (country,))
            personalCountry= await cursor.fetchone()
            return personalCountry

async def specificProfile(country: int):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            if (country!="admin"):
                await cursor.execute("""SELECT country, delegate1, delegate2, delegate3, delegate4, amendments_submitted, speaker_points from delegates WHERE id = %s""", (country,))
                specificCountry= await cursor.fetchone()
                return specificCountry
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
        
async def uniqueLogin():
    while True:
        randomNum = str(randrange(100000, 1000000)) #unhashed for now
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(
                    """SELECT exists (SELECT 1 FROM delegates WHERE login = %s LIMIT 1);""",
                    (randomNum,),
                )
                unique = await cursor.fetchone()
                if unique:
                    return randomNum
                
async def uniqueCountryID():
    while True:
        randomNum = str(randrange(100000, 1000000)) #unhashed for now
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(
                    """SELECT exists (SELECT 1 FROM delegates WHERE id = %s LIMIT 1);""",
                    (randomNum,),
                )
                unique = await cursor.fetchone()
                if unique:
                    return randomNum

# Add countries
@router.get("/sheet-export",status_code = status.HTTP_200_OK)
# async def sheetExport(token: Annotated[str, Depends(oauth2_scheme)]):
async def sheetExport():
    if True:
    # payload = get_current_user(token)
    # if payload.get("role") == roleList.get("admin"):
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
                            roleList.get("member"),
                        ),
                    )
            return data
    else:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized page"
            )

# update single country
@router.patch('/update-single-country',status_code = status.HTTP_200_OK)
# async def updateOneCountry(country: Country, token: Annotated[str, Depends(oauth2_scheme)]):
async def updateOneCountry(country: CountryPatch):
    #payload = get_current_user(token)
    
    #if payload.get("role") == roleList.get("admin") or payload.get("id") == country.id:
    if True:
        country = country.model_dump(exclude_unset=True)
        if country.get("id") is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Country name is required"
            )
        else: 
            async with pool.connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cursor:
                    query = """
                        UPDATE delegates
                        SET
                        country = COALESCE(%s, country),
                        delegate1 = COALESCE(%s, delegate1),
                        delegate2 = COALESCE(%s, delegate2),
                        delegate3 = COALESCE(%s, delegate3),
                        delegate4 = COALESCE(%s, delegate4),
                        role = COALESCE(%s, role),
                        login = COALESCE(%s, login),
                        amendments_submitted = COALESCE(%s, amendments_submitted),
                        speaker_points = COALESCE(%s, speaker_points)
                        WHERE id = %s
                        RETURNING *;
                        """
                    params = (
                        country.get("assigned_country"),
                        country.get("delegate1"),
                        country.get("delegate2"),
                        country.get("delegate3"),
                        country.get("delegate4"),
                        roleList.get(country.get("role")),
                        country.get("login"),
                        country.get("amendments_submitted"),
                        country.get("speaker_points"),
                        country.get("id"),
                    )
                    await cursor.execute(query, params)
                    result = await cursor.fetchone()
                    print(result)
            return result
    else: 
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized page"
        )

# add single country
@router.post('/add-single-country',status_code = status.HTTP_200_OK)
# async def addOneCountry(country: Country, token: Annotated[str, Depends(oauth2_scheme)]):
async def addOneCountry(country: Country):
    #payload = get_current_user(token)
    #if payload.get("role") == roleList.get("admin"):
    if True:
        try: 
            async with pool.connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cursor:
                    # country.login = await hash(country.login) gone for now
                    await cursor.execute('''INSERT INTO delegates (country, delegate1, delegate2, delegate3, delegate4, role, login, amendments_submitted, speaker_points) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *;''',
                                (country.assigned_country, country.delegate1,country.delegate2,country.delegate3,country.delegate4,roleList.get(country.role),country.login, country.amendments_submitted, country.speaker_points))
                    result = await cursor.fetchone() # removed the on conflict update instead itll throw uniqueviolation
            print(result)
            return result
        except UniqueViolation as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Country {country.assigned_country} already exists" # on insert must use error because of unique keyon delete add select no need 
            )
    else: 
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized page"
        )
        

@router.get("/get-countries", status_code = status.HTTP_200_OK)
# async def getAllCountries(token: Annotated[str, Depends(oauth2_scheme)]):
async def getAllCountries():
    #payload = get_current_user(token)
    #if payload.get("role") == roleList.get("admin") or payload.get("role") == roleList.get("member"):
    if True:
        allCount = await getCountriesGeneral()
        print(allCount)
        return allCount
    else: 
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized page"
        )  


@router.get("/select-country/{country}",status_code = status.HTTP_200_OK)
# async def selectCountry(country: str, token: Annotated[str, Depends(oauth2_scheme)]):
async def selectCountry(country: int):
    #payload = get_current_user(token)
    #if payload.get("role") == roleList.get("admin") or payload.get("role") == roleList.get("member"):
    if True:
        # if country == payload.get("id"):
        if True:
            result = await personalProfile(country)
        else:
            result = await specificProfile(country)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Country with name {country} was not found",
            )
        return result
    else: 
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized page"
        )  

@router.post("/set-exec", status_code = status.HTTP_200_OK)
async def setExec(person: Exec):
# async def setExec(person: Exec, token: Annotated[str, Depends(oauth2_scheme)]):
    #payload = get_current_user(token)
    #if payload.get("role") == roleList.get("admin"):
    if True:
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute('''INSERT INTO secretariat (name, position) VALUES (%s,%s) ON CONFLICT (name)
                            DO UPDATE SET name = EXCLUDED.name, position = EXCLUDED.position RETURNING *;''',
                            (person.name, person.position))
                return await cursor.fetchone()
    else: 
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized page"
        )  
        
@router.get("/get-secretariat", status_code = status.HTTP_200_OK)
async def getAllExecs():
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute("""SELECT name, position, id from secretariat""")
            allCount = await cursor.fetchall()
            return allCount
        
@router.delete('/delete-secretariat/{id}', status_code = status.HTTP_200_OK)
# async def setExec(name: str, token: Annotated[str, Depends(oauth2_scheme)]):
async def deleteExec(id: int):
    #payload = get_current_user(token)
    #if payload.get("role") == roleList.get("admin"):
    if True:
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute('''delete from secretariat where id = %s returning *''', (id,))
                result = await cursor.fetchone()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Name not found",
            )
        return result
    else: 
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized page"
        )
    
@router.patch('/update-secretariat', status_code = status.HTTP_200_OK)
# async def updateExec(exec: ExecPatch, token: Annotated[str, Depends(oauth2_scheme)]):
async def updateExec(exec: ExecPatch):
    #payload = get_current_user(token)
    #if payload.get("role") == roleList.get("admin"):
    if True:
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute('''UPDATE secretariat SET 
                                     name = COALESCE(%s, name),
                                     position = COALESCE(%s, position) WHERE id = %s RETURNING *''', (exec.id))
                result = await cursor.fetchone()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Name not found",
            )
        return result
            
    else: 
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized page"
        )

        
# delete
@router.delete("/select-country/{country}", status_code = status.HTTP_200_OK)
async def deleteCountry(country: int):
# async def deleteCountry(country: str, token: Annotated[str, Depends(oauth2_scheme)]):
    #payload = get_current_user(token)
    #if payload.get("role") == roleList.get("admin"):
    if True:
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(
                    """DELETE FROM delegates WHERE id = %s RETURNING *""", (country,)
                )
                result = await cursor.fetchone()
                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Country not found",
                    )
                return {"message": f"{country} deleted"}
    else: 
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized page"
        )
        
# need to make so that admin country is untouchable