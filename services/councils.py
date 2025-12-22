from db.utils import fetch_all, fetch_one, transaction, execute
from typing import Any
from fastapi import HTTPException, status

async def get_all_councils_service() -> list[dict[str, Any]]:
    result = await fetch_all('''SELECT council_id, name, resolution_count from councils''')
    return result

async def get_main_council_service() -> dict[str, Any] | None:
    result = await fetch_one('''SELECT council_id, name, resolution_count from councils WHERE is_main = TRUE''')
    return result

async def post_council_service(name: str, resolution_count: int) -> dict[str,Any]:
    result = await fetch_one('''INSERT INTO councils (name, resolution_count) VALUES (%s,%s) RETURNING name, resolution_count, council_id;''', (name, resolution_count))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create council",
        )
    return result

async def delete_council_service(council_id: int) -> dict[str, Any]:
    result = await fetch_one('''DELETE FROM council WHERE council_id = %s RETURNING name, resolution_count, council_id''', (council_id,))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Council not found",
        )
    return result

async def update_council_service(name: str | None, resolution_count: int | None, council_id: int) -> dict[str, Any]:
    result = await fetch_one('''UPDATE council SET name = COALESCE(%s, name), resolution_count = COALESCE(%s, resolution_count) WHERE council_id = %s RETURNING *''', (name, resolution_count, council_id,))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Council not found",
        )
    return result

async def update_main_council_service(council_id: int) -> dict[str, Any]:
    async with transaction() as cursor:
        await execute('''UPDATE councils SET is_main = FALSE WHERE is_main = TRUE;''', cursor=cursor)
        result = await fetch_one('''UPDATE councils SET is_main = TRUE WHERE council_id = %s;''',(council_id,), cursor=cursor)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Council not found",
        )
    return result