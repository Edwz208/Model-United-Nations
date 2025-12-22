from fastapi import HTTPException, status
from psycopg.errors import (
    UniqueViolation,
    ForeignKeyViolation,
    CheckViolation
)
from psycopg.rows import dict_row
from contextlib import asynccontextmanager
from db.connection import get_async_pool  
from typing import Any

_pool = None

async def get_pool():
    global _pool
    if _pool is None:
        _pool = get_async_pool()
    return _pool

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
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            try:
                yield cursor
            except Exception as e:
                handle_db_error(e)

@asynccontextmanager
async def transaction():
    pool = await get_pool()
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

async def fetch_one(query: str, params: tuple[Any, ...] = (), cursor=None):
    if cursor:
        await cursor.execute(query, params)  # type: ignore
        return await cursor.fetchone()

    async with get_cursor() as cur:
        await cur.execute(query, params)  # type: ignore
        return await cur.fetchone()


async def fetch_all(query: str, params: tuple[Any, ...] = (), cursor=None):
    if cursor:
        await cursor.execute(query, params)  # type: ignore
        return await cursor.fetchall()

    async with get_cursor() as cur:
        await cur.execute(query, params)  # type: ignore
        return await cur.fetchall()


async def execute(query: str, params: tuple[Any, ...] = (), cursor=None):
    if cursor:
        return await cursor.execute(query, params)  # type: ignore

    async with get_cursor() as cur:
        return await cur.execute(query, params)  # type: ignore

