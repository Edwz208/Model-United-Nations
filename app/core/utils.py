# app/core/utils.py

import re
from fastapi import UploadFile
from pathlib import Path
import shutil
from uuid import uuid4
from app.core.exceptions import InvalidUploadException

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
        raise InvalidUploadException("PDFs only")
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        print(f"Failed to save file: {e}")
        raise InvalidUploadException("Failed to save file")
    return unique_name
