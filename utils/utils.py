import re
from fastapi import UploadFile, HTTPException, status
from pathlib import Path
import shutil
from uuid import uuid4

def sanitize_key(key: str) -> str:
    return key.strip().lower().replace("#", "").replace(" ", "_")

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\-.]', '_', name)

def file_to_directory(file: UploadFile) -> str | None:
    if file == None or file.filename == None:
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