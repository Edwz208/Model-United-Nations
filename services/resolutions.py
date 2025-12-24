from db.utils import fetch_all, fetch_one, transaction, execute
from utils.utils import sanitize_filename
from typing import Any
from fastapi import HTTPException, status
from pathlib import Path

async def get_all_resolutions_general_info_service() -> list[dict[str, Any]]:
    result = await fetch_all('''SELECT number, title, clauses, council_id, status, amendment_count, resolution_id FROM resolutions''')
    return result

async def get_all_council_resolutions_general_info_service(council_id: int) -> list[dict[str, Any]]:
    result = await fetch_all('''SELECT number, title, clauses, status, amendment_count, resolution_id, council_id FROM resolutions WHERE council_id = %s''', (council_id,))
    return result

async def get_specific_resolution_service(resolution_id: int) -> dict[str, Any]:
    resolution = await fetch_one('''SELECT number, title, clauses, status, council_id, amendment_count, resolution_id, submitter, seconder, negator FROM resolutions WHERE resolution_id = %s''', (resolution_id,))
    if not resolution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resolution not found")
    return resolution

async def delete_resolution_service(resolution_id: int) -> dict[str, Any]:
    async with transaction() as cursor:
        url = await fetch_one('''SELECT url FROM resolutions WHERE resolution_id=%s''', (resolution_id,), cursor=cursor)
        if url and url.get("url"):
            file = Path(f'./uploads/resolutions/{url.get("url")}')
            file.unlink()
        result = await fetch_one('''DELETE FROM resolutions WHERE resolution_id=%s RETURNING *''' , (resolution_id,), cursor=cursor)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resolution {resolution_id} was not found",
            )
        await execute('''UPDATE councils SET resolution_count = resolution_count-1 WHERE council_id = %s RETURNING resolution_count''', (result.get('council_id'),), cursor=cursor)
    return result
    
