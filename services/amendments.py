from db.utils import fetch_one, fetch_all
from typing import Any
from fastapi import HTTPException, status

async def get_own_amendments_service(id: int) -> list[dict[str, Any]]:
    result = await fetch_all('''SELECT content,clause,resolution_id,submitter,status, modified_at, amendment_id FROM amendments WHERE (%s) = ANY(submitter)''', (id,))
    return result
        
async def get_recent_amendments() -> list[dict[str, Any]]:
    result = await fetch_all('''SELECT content, clause, resolution_id, submitter, status, modified_at, amendment_id FROm amendments ORDER BY modified_at DESC LIMIT 3''')
    return result

async def get_all_amendments_for_resolution_service(resolution_id: int) -> list[dict[str, Any]]:
    result = await fetch_all('''SELECT content,clause,resolution_id,submitter,status, modified_at, amendment_id FROM amendments WHERE resolution_id = %s''', (resolution_id,))
    return result

async def upload_amendment_service(content: str, clause: int, resolution_id: int, submitter: int, amendment_status: str) -> dict[str, Any]:
    result = await fetch_one('''WITH updated AS (UPDATE resolutions SET resolution_count = resolution_count + 1 WHERE resolution_id = %s) INSERT INTO amendments (content, clause, resolution_id, submitter, status) SELECT %s,%s,%s,%s,%s FROM resolutions r JOIN country_council cc on cc.council_id = r.council_id WHERE resolution_id = %s AND cc.country_id = %s RETURNING *''', 
                                (resolution_id, content, clause, resolution_id, submitter, amendment_status, resolution_id, submitter))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to upload amendment",
        )
    return result

async def delete_amendment_service(amendment_id: int) -> dict[str, Any]:
    result = await fetch_one('''WITH delete_amendment AS (DELETE FROM amendments WHERE amendment_id= %s RETURNING *), update_resolutions AS (UPDATE resolutions SET amendment_count = amendment_count -1 WHERE resolution_id = (SELECT resolution_id FROM delete_amendment)) SELECT * FROM delete_amendment''', (amendment_id,))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete amendment",
        )
    return result

async def approve_reject_amendment_service(amendment_id: int, amendment_status: str, rejection_message: str | None) -> dict[str, Any]:
    match amendment_status:
        case 'rejected':
            result = await fetch_one('''UPDATE amendments SET resolution=''', (amendment_id, amendment_status, rejection_message,))
        case 'approved':
            result = await fetch_one('''''', (amendment_id, amendment_status))
        case 'pending':
            result = await fetch_one('''''', (amendment_id, amendment_status))
        case _:
            result = None
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to approve/reject amendment",
        )
    return result

async def update_amendment_service(amendment_id: int, resolution_id: int | None, amendment_status: str | None, clause: int | None, submitter: int | None, content: str | None) -> dict[str, Any]:
    result = await fetch_one('''UPDATE amendments SET resolution_id = COALESCE(%s, resolution_id), status = COALESCE(%s, status), clause = COALESCE(%s, clause), submitter = COALESCE(%s, submitter), content = COALESCE(%s, content) WHERE amendment_id = %s RETURNING *''', (resolution_id, amendment_status, clause, submitter, content, amendment_id))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update amendment",
        )
    return result