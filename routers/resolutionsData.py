from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from db import get_async_pool
from pydantic import ValidationError
from psycopg.rows import dict_row
from schemas import Resolution
import shutil
from pathlib import Path
from uuid import uuid4
import re


def sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\-.]', '_', name)

pool = get_async_pool()
router = APIRouter()

@router.post('/upload-resolution',status_code = status.HTTP_200_OK)
async def uploading_resolution(
    council: int = Form(...),
    title: str = Form(...),
    seconder: str = Form(...),
    clauses: int = Form(...),
    submitter: str = Form(...),
    negator: str = Form(...),
    file: UploadFile = File(...),
    number: int = Form(...)
):
    file_folder = Path("./uploads/resolutions")
    file_folder.mkdir(parents=True, exist_ok=True)
    unique_name = sanitize_filename(f"{uuid4()}_{file.filename}")
    
    file_location = file_folder / unique_name
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="PDFs only")
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        print(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")
    url = str(file_location)
    try:
        resolutionData = Resolution(council=council,title = title, clauses=clauses, status="pending", submitter = submitter, seconder=seconder, negator=negator, number=number)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute('''INSERT INTO resolutions (council_id, title, url, number, clauses, submitter, seconder, negator, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) returning *''', 
                           (council,title,url,number*council,clauses,submitter,seconder,negator,"pending"))
            addedRes = await cursor.fetchone()
    return {"resolution": addedRes}
    
        
