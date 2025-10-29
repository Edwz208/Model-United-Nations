from fastapi import APIRouter, status, HTTPException, Response, Request
from authentication import decode, generateJwt, SECRET_KEY, REFRESH_KEY, REFRESH_TOKEN_EXPIRE_MINUTES, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import User
from db import get_async_pool
from psycopg.rows import dict_row
router = APIRouter()
from .amendmentsData import getOwnAmendments, getRecentAmendments

pool = get_async_pool()


@router.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def login(user: User, response: Response) -> dict:
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(
                """SELECT login, country, role, id from delegates WHERE country = %s""",
                (user.country.lower().capitalize(),),
            )
            returned_info = await cursor.fetchone()
            if not returned_info or (not user.code == returned_info["login"]):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invalid credes",
                ) # removed hash check for now
            
            del returned_info["login"]
            returned_info.update({"accessToken": generateJwt(returned_info, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES)})
            response.set_cookie(key="refresh_token",value=generateJwt(returned_info, REFRESH_KEY, REFRESH_TOKEN_EXPIRE_MINUTES), httponly=True, secure=False, samesite="lax", path="/refresh")
            returned_info["recentAmendments"] = await getRecentAmendments()
            returned_info["ownAmendments"] = await getOwnAmendments(returned_info["id"])
            print(returned_info)
            return returned_info # set secure cookie once not in dev
    

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,         
        samesite="lax",     
        path="/refresh"   )       
    print("cookie deleted")
    
    return {"accessToken": ""}


@router.get("/refresh")
async def refresh_token(request: Request):
    token = request.cookies.get("refresh_token")
    print(f"Refresh token from cookies: {token}")
    payload = await decode(token, REFRESH_KEY)
    print(payload)
    if token:
        newAccess = generateJwt(payload, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES)
        recentAmendments = await getRecentAmendments()
        ownAmendments = await getOwnAmendments(payload["id"])
        return {"accessToken": newAccess, "role": payload["role"], "country": payload["country"], "id": payload["id"],"ownAmendments": ownAmendments, "recentAmendments": await recentAmendments}
    else:
        raise HTTPException(status_code=401, detail="Missing refresh token")

# general page, return the personal profile of the country, own amendments, recent amendments added
# general amendments page
# general resolutions page
# general general countries page

# admin dashboard, return all resolutions general, amendments general, countries general 
