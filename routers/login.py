from fastapi import APIRouter, status, HTTPException
from authentication import verify, hash
from schemas import User
from db import get_async_pool
from psycopg.rows import dict_row

router = APIRouter()

pool = get_async_pool()
@router.post("/login")
async def login(user: User):   
    hashed_login = hash(user.code)
    print(user.code)
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(
                        """SELECT country, role from delegates WHERE login = %s """,
                        (user.code,),
                )
                returned_info = await cursor.fetchone()
                print(returned_info)
                if not returned_info:
                        raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
                        )
                print(returned_info)
                return returned_info
