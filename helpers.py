from authentication import get_current_user
from fastapi import HTTPException, status, Depends
from psycopg.errors import (
    UniqueViolation,
    ForeignKeyViolation,
    CheckViolation
)
from psycopg.rows import dict_row
from contextlib import asynccontextmanager
from db import get_async_pool  
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pool = get_async_pool

async def require_admin(token: str = Depends(oauth2_scheme)):
    payload = await get_current_user(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return payload

async def require_member_or_admin(token: str = Depends(oauth2_scheme)):
    payload = await get_current_user(token)
    if payload.get("role") not in ["admin", "member"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return payload

async def require_specific_member_or_admin(id: int, token: str = Depends(oauth2_scheme)):
    payload = await get_current_user(token)
    if payload.get("role") != "admin" and payload.get("id") == id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return payload

def handle_db_error(e: Exception):
    if isinstance(e, UniqueViolation):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unique constraint violation."
        )
    if isinstance(e, ForeignKeyViolation):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reference (foreign key violation)."
        )
    if isinstance(e, CheckViolation):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Value violates a CHECK constraint."
        )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database error."
    )       

@asynccontextmanager
async def get_cursor():
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            try:
                yield cursor
            except Exception as e:
                handle_db_error(e)

@asynccontextmanager
async def transaction():
    async with pool.connection() as conn:
        try:
            await conn.execute("BEGIN")
            async with conn.cursor(row_factory=dict_row) as cursor:
                yield cursor
            await conn.execute("COMMIT")
        except Exception as e:
            await conn.execute("ROLLBACK")
            handle_db_error(e)
            raise

async def fetch_one(query: str, params: tuple = (), cursor=None):
    if cursor:
        await cursor.execute(query, params)
        return await cursor.fetchone()

    async with get_cursor() as cur:
        await cur.execute(query, params)
        return await cur.fetchone()


async def fetch_all(query: str, params: tuple = (), cursor=None):
    if cursor:
        await cursor.execute(query, params)
        return await cursor.fetchall()

    async with get_cursor() as cur:
        await cur.execute(query, params)
        return await cur.fetchall()


async def execute(query: str, params: tuple = (), cursor=None):
    if cursor:
        return await cursor.execute(query, params)

    async with get_cursor() as cur:
        return await cur.execute(query, params)