from fastapi import APIRouter, status, HTTPException, Response
from authentication import verify, generateJwt
from schemas import User
from db import get_async_pool
from psycopg.rows import dict_row

router = APIRouter()

pool = get_async_pool()

roleList = {"member": 2007, "admin": 4015}


@router.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def login(user: User, response: Response):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            user.country = user.country.lower().capitalize()
            print(user.code)
            await cursor.execute(
                """SELECT login, country, role from delegates WHERE country = %s""",
                (user.country,),
            )
            returned_info = await cursor.fetchone()
            if not returned_info or (not await verify(user.code, returned_info["login"]) and not user.code==returned_info["login"]):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invalid credes",
                )
            del returned_info["login"]
            returned_info["role"] = [roleList[returned_info["role"]]]
            returned_info.update({"accessToken": generateJwt(returned_info, response)})
            return returned_info
