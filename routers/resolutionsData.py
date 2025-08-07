from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Depends
from db import get_async_pool
from pydantic import ValidationError
from psycopg.rows import dict_row
from schemas import Resolution, ResolutionPatch
import shutil
from pathlib import Path
from uuid import uuid4
import re
from typing import Annotated, Optional
from psycopg.errors import UniqueViolation, ForeignKeyViolation
from authentication import roleList, get_current_user
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") #token url only for swagger 

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\-.]', '_', name)

pool = get_async_pool()
router = APIRouter()

def fileToDirectory(file: UploadFile):
    if file == None:
        return None
    file_folder = Path("./uploads/resolutions")
    file_folder.mkdir(parents=True, exist_ok=True)
    unique_name = sanitize_filename(f"{uuid4()}_{file.filename}")
    file_location = file_folder / unique_name
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="PDFs only")
    try:
        with open(file_location, "wb") as buffer: # if fails fastapi will auto cancel rest of function
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        print(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")
    return unique_name

async def getResolutionsGeneral():
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute('''SELECT number, title, clauses, council_id, status, amendment_count from resolutions''')
            allResolutions = await cursor.fetchall()
            return allResolutions
        

@router.get('/get-resolutions-general', status_code=status.HTTP_200_OK)
# async def genResolutionsRoute(token: Annotated[str, Depends(oauth2_scheme)]):
async def genResolutionsRoute():
    # payload = get_current_user(token)
    # if payload.get("role") == roleList.get("admin") or payload.get("role") == roleList.get("member"):
    if True: 
        resolutions = await getResolutionsGeneral() #doesnt let continuing through function compared to create_task asyncio
        return resolutions
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view resolutions")
    
@router.get('/get-resolution/{number}', status_code=status.HTTP_200_OK)
# async def specificResolution(token: Annotated[str, Depends(oauth2_scheme)], number: int):
async def specificResolution(number: int):
    # payload = get_current_user(token)
    # if payload.get("role") == roleList.get("admin") or payload.get("role") == roleList.get("member"):
    if True:
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute('''SELECT * from resolutions WHERE number = %s''', (number,))
                resolution = await cursor.fetchone()
                if not resolution:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resolution not found")
                return resolution
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view resolutions")
        
@router.post('/upload-resolution',status_code = status.HTTP_200_OK)
# async def uploading_resolution(
#     token: Annotated[str, Depends(oauth2_scheme)], #put non default arguments before default arguments Depends is non deafult
#     council: int = Form(...),
#     title: str = Form(...),
#     seconder: str = Form(...),
#     clauses: int = Form(...),
#     submitter: str = Form(...),
#     negator: str = Form(...),
#     file: UploadFile = File(...),
#     number: int = Form(...)
# ):
async def uploading_resolution(
    council: int = Form(...),
    title: str = Form(...),
    seconder: str = Form(...),
    clauses: int = Form(...),
    submitter: str = Form(...),
    negator: str = Form(...),
    file: UploadFile = File(...),
):
    # payload = get_current_user(token)
    # if payload.get("role") == roleList.get("admin"):
    if True:
        url = fileToDirectory(file)
        try:
            resolutionData = Resolution(council=council,title = title, clauses=clauses, status="pending", submitter = submitter, seconder=seconder, negator=negator)
        except ValidationError as e: # auto pydantic handling only done if in direct call to endpoint
            raise HTTPException(status_code=422, detail=e)
        try: 
            async with pool.connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cursor:
                    await cursor.execute('''UPDATE councils SET resolution_count = resolution_count + 1 WHERE id = %s RETURNING *''', (1,))
                    number = await cursor.fetchone()
                    print(number)
                    print("asgaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                    resolution_id = f'{council}{number.get('resolution_count')}'
                    print("resolution_id",resolution_id)
                    await cursor.execute('''INSERT INTO resolutions (council_id, title, url, number, clauses, submitter, seconder, negator) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) returning *''', 
                                (council,title,url,int(resolution_id),clauses,submitter,seconder,negator))
                    addedRes = await cursor.fetchone()
            return {"resolution": addedRes}
        except UniqueViolation:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Resolution with this number/title already exists")
        except ForeignKeyViolation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Council/Country not found")
    else: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to upload resolutions")
        
# delete resolution

@router.delete('/delete-resolution/{number}', status_code=status.HTTP_200_OK)
# async def deleteResolution(token: Annotated[str, Depends(oauth2_scheme)], number: int):
async def deleteResolution(number: int):
    # payload = get_current_user(token)
    # if payload.get("role") == roleList.get("admin"):
    if True:
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute('''SELECT url from resolutions WHERE number=%s''', (number,))
                url = await cursor.fetchone()
                file = Path('./uploads/resolutions/'+ url.get("url"))
                print(file)
                file.unlink()
                await cursor.execute('''DELETE from resolutions WHERE number=%s RETURNING *''' , (number,))
                result = await cursor.fetchall()
                await cursor.execute('''UPDATE councils SET resolution_count = resolution_count-1 WHERE id = %s RETURNING resolution_count''', (result.get('council_id'),))
                print(result)
                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Resolution {number} was not found",
                    )
                return result
    else: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete resolutions")
    
@router.patch('/update-resolution/{number}')
# async def updateResolution(token: Annotated[str, Depends(oauth2_scheme)], number: int, resolution: ResolutionPatch):
async def updateResolution(number: int, council_id: Optional[int] = Form(None), title: Optional[str] = Form(None), clauses: Optional[int] = Form(None), submitter: Optional[str] = Form(None), seconder: Optional[str] = Form(None), negator: Optional[str] = Form(None), status: Optional[str] = Form(None), file: UploadFile = File(None)):
    # payload = get_current_user(token)
    # if payload.get("role") == roleList.get("admin"):
    if True: 
        url = fileToDirectory(file)
        try: 
            resolution = ResolutionPatch(title=title, council_id=council_id, clauses=clauses, submitter=submitter, seconder=seconder, negator=negator,status=status, url=url)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=e) 
        resolution = resolution.model_dump(exclude_unset=True) #converts to dict
        async with pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''UPDATE resolutions SET 
                                     title = COALESCE(%s, title),
                                     council_id = COALESCE(%s, council_id), 
                                     status=COALESCE(%s, status), 
                                     clauses= COALESCE(%s, clauses), 
                                     submitter = COALESCE(%s, submitter), 
                                     seconder = COALESCE(%s, seconder), 
                                     negator = COALESCE(%s, negator), 
                                     url = COALESCE(%s, url)
                                     WHERE (number) = %s RETURNING *''', (resolution.get('title'),resolution.get('council_id'),resolution.get('status'), resolution.get('clauses'), resolution.get('submitter'), resolution.get('seconder'), resolution.get('negator'), resolution.get('url'), number))
                result = await cursor.fetchone()
                print(result)
                return result

    else: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update resolutions")  

