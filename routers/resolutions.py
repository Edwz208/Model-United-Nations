from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Depends
from backend.db.connection import get_async_pool
from pydantic import ValidationError
from psycopg.rows import dict_row
from schemas import Resolution, ResolutionPatch
import shutil
from uuid import uuid4
from typing import Annotated, Optional
from services.resolutions import get_all_resolutions_general_info_service, get_all_council_resolutions_general_info_service, get_specific_resolution_service, delete_resolution_service
from auth.dependencies import require_admin, require_member_or_admin
from typing import Any

# For resolutions, we allow admin to change the order of resolutions, change the order of multiple at once after saving to make it one call to the server

pool = get_async_pool()
router = APIRouter()

def fileToDirectory(file: UploadFile) -> str:
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

        

@router.get('/get-all-resolutions-general-info', status_code=status.HTTP_200_OK)
async def get_all_resolutions_general_info(current_user=Depends(require_member_or_admin)) -> list[dict[str, Any]]:
    result = await get_all_resolutions_general_info_service()
    return result

@router.get('/get-all-resolutions-general-info/{council_id}', status_code=status.HTTP_200_OK)
async def get_council_all_resolutions_general_info(council_id: int, current_user=Depends(require_member_or_admin)) -> list[dict[str, Any]]:
    result = await get_all_council_resolutions_general_info_service(council_id)
    return result

@router.get('/get-resolution/{resolution_id}}', status_code=status.HTTP_200_OK)
async def specific_resolution(resolution_id: int, current_user=Depends(require_member_or_admin)):
    resolution = await get_specific_resolution_service(resolution_id)
    return resolution


@router.post('/upload-resolution',status_code = status.HTTP_200_OK)
async def uploading_resolution(#put non default arguments before default arguments Depends is non deafult
    council_id: str = Form(...),
    title: str = Form(...),
    clauses: str = Form(...),
    submitter: str = Form(...),
    seconder: str = Form(...),
    negator: str = Form(...),
    file: UploadFile = File(...),
    current_user = Depends(require_admin)
    # missing status, amendment_count
):
    url = fileToDirectory(file)
    try:
        print('hi')
        resolutionData = Resolution(council_id=council_id,title = title, clauses=clauses, submitter=submitter, seconder=seconder, negator=negator)
    except ValidationError as e: # auto pydantic handling only done if in direct call to endpoint
        raise HTTPException(status_code=422, detail=e)
    try: 
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute('''UPDATE councils SET resolution_count = resolution_count + 1 WHERE council_id = %s RETURNING *''', (council_id,))
                number = await cursor.fetchone()
                if len(number.get('resolution_count')) == 1:
                    number['resolution_count'] = f"0{number.get('resolution_count')}"
                if len(council_id) == 1:
                    council_id_as_string = f'0{council_id}'
                resolution_id = f"{council_id_as_string}{number.get('resolution_count')}"
                print("resolution_id",resolution_id)
                await cursor.execute('''INSERT INTO resolutions (council_id, title, url, number, clauses, submitter, seconder, negator) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) returning *''', 
                            (council_id,title,url,int(resolution_id),clauses,submitter,seconder,negator))
                addedRes = await cursor.fetchone()
        return {"resolution": addedRes}
    
@router.delete('/delete-resolution/{resolution_id}', status_code=status.HTTP_200_OK)
async def delete_resolution(resolution_id: int, current_user=Depends(require_admin)) -> dict[str, Any]:
    result = await delete_resolution_service(resolution_id)   
    return result
    
@router.patch('/update-resolution/{number}')
async def updateResolution(token: Annotated[str, Depends(oauth2_scheme)], number: str, council_id: Optional[str] = Form(None), title: Optional[str] = Form(None), clauses: Optional[int] = Form(None), submitter: Optional[str] = Form(None), seconder: Optional[str] = Form(None), negator: Optional[str] = Form(None), status: Optional[str] = Form(None), file: UploadFile = File(None)):
    payload = await get_current_user(token)
    if payload.get("role") == 'admin':
        url = fileToDirectory(file)
        try: 
            resolution = ResolutionPatch(title=title, council_id=council_id, clauses=clauses, submitter=submitter, seconder=seconder, negator=negator,status=status, url=url)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=e) 
        resolution = resolution.model_dump(exclude_unset=True) #converts to dict
        async with pool.connection() as conn:
            async with conn.cursor() as cursor:
                    new_number = f'{council_id}{number[2]}{number[3]}'
                    await cursor.execute('''UPDATE resolutions SET 
                                     title = COALESCE(%s, title),
                                     council_id = COALESCE(%s, council_id), 
                                     status=COALESCE(%s, status), 
                                     clauses= COALESCE(%s, clauses), 
                                     submitter = COALESCE(%s, submitter), 
                                     seconder = COALESCE(%s, seconder), 
                                     negator = COALESCE(%s, negator), 
                                     url = COALESCE(%s, url),
                                     number = COALESCE(%s, number)
                                     WHERE (number) = %s RETURNING *''', (resolution.get('title'),resolution.get('council_id'),resolution.get('status'), resolution.get('clauses'), resolution.get('submitter'), resolution.get('seconder'), resolution.get('negator'), resolution.get('url'), new_number, number))
                    result = await cursor.fetchone()
                    print(result)
                    return result
    else: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update resolutions")  
