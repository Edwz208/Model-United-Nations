from fastapi import APIRouter, status, HTTPException
from authentication import verify
from schemas import User
from db import get_async_pool
from psycopg.rows import dict_row

router = APIRouter()

pool = get_async_pool()


@router.post("/login", status_code = status.HTTP_202_ACCEPTED)
async def login(user: User):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute("""SELECT login from delegates""")
            codes = await cursor.fetchall()

            for code in codes:
                print(code["login"])
                if await verify(user.code, code["login"]):
                    print("true")
                    await cursor.execute(
                        """SELECT country, role from delegates WHERE login = %s """,
                        (code["login"],),
                    )
                    returned_info = await cursor.fetchone()
                    return returned_info
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
            )
