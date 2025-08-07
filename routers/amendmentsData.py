from fastapi import APIRouter, HTTPException, status, Depends
from db import get_async_pool
from psycopg.rows import dict_row
from schemas import Amendment, AmendmentPatch
from psycopg.errors import ForeignKeyViolation
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from authentication import get_current_user, roleList
pool = get_async_pool()
router = APIRouter()

async def getOwnAmendments(country: int):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute("""WITH country_name as (SELECT country from delegates WHERE id=%s) SELECT content,clause,resolution_id,submitter,status,resolution_title, modified_at from amendments WHERE (SELECT country from country_name) = ANY(submitter)""", (country,))
            ownAmendments = await cursor.fetchall()
            return ownAmendments
        
async def getRecentAmendments():
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute("""SELECT content, clause, resolution_id, submitter, status, resolution_title, modified_at from amendments ORDER BY modified_at DESC LIMIT 3""")
            recentAmendments = await cursor.fetchall()
            return recentAmendments
        
@router.get('/specific-amendment-country/{country}', status_code=status.HTTP_200_OK)
# async def specificCountryAmendment(token: Annotated[str, Depends(oauth2_scheme)], country: str):
async def specificCountryAmendment(country: int):
    # payload = get_current_user(token)
    # if payload.get("role") == roleList.get("admin") or payload.get("role") == roleList.get("member"):
    if True:
        amendments = await getOwnAmendments(country)
        return amendments
    else: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view amendments")

@router.get('/all-amendments', status_code=status.HTTP_200_OK)
# async def allAmendments(token: Annotated[str, Depends(oauth2_scheme)]):
async def allAmendments():
    # payload = get_current_user(token)
    # if payload.get("role") == roleList.get("admin") or payload.get("role") == roleList.get("member"):
    if True:
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute('''SELECT content, clause, resolution_id, submitter, status, resolution_title, modified_at from amendments''')
                result = await cursor.fetchall()
                print(result)
        return result
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view amendments")
        


@router.post('/upload-amendment',status_code = status.HTTP_200_OK)
# async def uploading_amendment(amendment: Amendment, token: Annotated[str, Depends(oauth2_scheme)]):
async def uploading_amendment(amendment: Amendment):
    print("hi")
    # payload = get_current_user(token)
    # if payload.get("role") == roleList.get("admin") or payload.get("role") == roleList.get("member"):
    print(amendment.resolution_title)
    if True:
        try: 
            async with pool.connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cursor:
                    await cursor.execute('''UPDATE resolutions SET amendment_count = amendment_count +1 WHERE number = %s RETURNING amendment_count''', (amendment.resolution_id,))
                    amendment_count = await cursor.fetchone()
                    print(amendment_count.get("amendment_count"))
                    amendment_id = f"{amendment.resolution_id}{amendment_count.get('amendment_count')}"
                    await cursor.execute('''INSERT INTO amendments (content, clause, resolution_id, submitter, status, resolution_title, amendment_id) VALUES (%s,%s,%s,%s,%s,%s,%s) returning *''', 
                                (amendment.content, amendment.clause, amendment.resolution_id, amendment.submitter, amendment.status, amendment.resolution_title, amendment_id))
                    addedAmendment = await cursor.fetchone()
            return addedAmendment
        except ForeignKeyViolation:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Amendment not found")
    else: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to upload amendments")
    

@router.patch('/update-amendment/{number}')
async def updateAmendment(token: Annotated[str, Depends(oauth2_scheme)], number: int, amendment: AmendmentPatch):
# async def updateAmendment(number: int, amendment: AmendmentPatch):
    payload = get_current_user(token)
    if payload.get("role") == roleList.get("member"):
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute('''WITH country_name as (SELECT country from delegates WHERE id=%s) UPDATE amendments SET 
                                     content=COALESCE(%s, content), 
                                     clause = COALESCE(%s, clause), 
                                    submitter = COALESCE(%s, submitter), 
                                     status = COALESCE(%s, status) WHERE amendment_id = %s and (select country from country_name) =ANY(submitter) RETURNING *''',
                                     (payload.get("id"),amendment.content, amendment.clause, amendment.submitter, amendment.status, number))
                result = await cursor.fetchone()
    # if payload.get("role") == roleList.get("admin"):
    elif True:
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute('''UPDATE amendments SET 
                                     content=COALESCE(%s, content), 
                                     clause = COALESCE(%s, clause), 
                                    submitter = COALESCE(%s, submitter), 
                                     status = COALESCE(%s, status) WHERE amendment_id = %s RETURNING *''',
                                     (amendment.content, amendment.clause, amendment.submitter, amendment.status, number))
                result = await cursor.fetchone()
    else: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update amendments")
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Amendment was not found",
        )
    return result
        
@router.delete('/delete-amendment/{number}', status_code=status.HTTP_200_OK)
async def deleteAmendment(token: Annotated[str, Depends(oauth2_scheme)], number: int):
# async def deleteAmendment(number: int):
    payload = get_current_user(token)
    if payload.get("role") == roleList.get("member"):
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute('''WITH country_name as (SELECT country from delegates WHERE id=%s), deleteAmend as (DELETE from amendments WHERE amendment_id=%s and (select country from country_name) =ANY(submitter) RETURNING * ), updateResolution as (UPDATE resolutions SET amendment_count = amendment_count -1 WHERE number = (select resolution_id from deleteAmend)) select * from deleteAmend''', (payload.get("id"),number,))
                result = await cursor.fetchone()
    elif payload.get("role") == roleList.get("admin"):
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute('''WITH deleteAmend as (DELETE from amendments WHERE amendment_id=%s RETURNING *), updateResolutions as (UPDATE resolutions SET amendment_count = amendment_count -1 WHERE number = (select resolution_id from deleteAmend)) select * from deleteAmend''', (number,))
                result = await cursor.fetchone() # use temporary tables (CTEs) for returning query cannot have subqueries within return statements
    else: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete the amendment")
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resolution {number} was not found",
        )
    return result