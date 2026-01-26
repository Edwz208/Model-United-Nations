from fastapi import HTTPException, status
from psycopg.errors import (
    UniqueViolation,
    ForeignKeyViolation,
    CheckViolation,
    NotNullViolation,
    InvalidTextRepresentation,
    DatatypeMismatch,
    UndefinedColumn,
    UndefinedTable,
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
    print("DB ERROR TYPE:", type(e))
    print("DB ERROR REPR:", repr(e))

    if isinstance(e, UniqueViolation):
        raise HTTPException(status_code=409, detail="Unique constraint violation.")
    if isinstance(e, ForeignKeyViolation):
        raise HTTPException(status_code=422, detail="Invalid reference (foreign key violation).")
    if isinstance(e, CheckViolation):
        raise HTTPException(status_code=422, detail="Value violates a CHECK constraint.")
    if isinstance(e, NotNullViolation):
        raise HTTPException(status_code=422, detail="Missing required field (NOT NULL).")
    if isinstance(e, (InvalidTextRepresentation, DatatypeMismatch)):
        raise HTTPException(status_code=422, detail="Invalid data type.")
    if isinstance(e, (UndefinedColumn, UndefinedTable)):
        raise HTTPException(status_code=500, detail="Database schema mismatch.")

    raise HTTPException(status_code=500, detail=f"Database error: {type(e).__name__}")


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

