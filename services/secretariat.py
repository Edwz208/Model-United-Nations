from db.utils import fetch_all, fetch_one, transaction, execute
from typing import Any
from fastapi import HTTPException, status

async def post_exec_service(name: str, position: str) -> dict[str, Any]:
    execSet = await fetch_one('''INSERT INTO secretariat (name, position) VALUES (%s,%s) RETURNING name, position, secretariat_id;''', (name, position))
    if not execSet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create exec",
        )
    return execSet

async def delete_exec_service(secretariat_id: int) -> dict[str, Any]:
    result = await fetch_one('''DELETE FROM secretariat WHERE secretariat_id = %s RETURNING name, position, secretariat_id''', (secretariat_id,))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Secretariat not found",
        )
    return result

async def update_exec_service(name: str | None, position: str | None, secretariat_id: int) -> dict[str, Any]:
    result = await fetch_one('''UPDATE secretariat SET name = COALESCE(%s, name), position = COALESCE(%s, position) WHERE secretariat_id = %s RETURNING *''', (name, position, secretariat_id,))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Secretariat not found",
        )
    return result