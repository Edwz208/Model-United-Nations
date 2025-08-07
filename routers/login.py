from fastapi import APIRouter, status, HTTPException, Response, Request
from authentication import verify, decode, generateJwt, roleList,SECRET_KEY, REFRESH_KEY, REFRESH_TOKEN_EXPIRE_MINUTES, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import User
from db import get_async_pool
from psycopg.rows import dict_row
import asyncio
router = APIRouter()
from .countryData import personalProfile, specificProfile
from .amendmentsData import getOwnAmendments, getRecentAmendments

pool = get_async_pool()


@router.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def login(user: User, response: Response):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            user.country = user.country.lower().capitalize()
            print(user.code)
            await cursor.execute(
                """SELECT login, country, role, id from delegates WHERE country = %s""",
                (user.country,),
            )
            returned_info = await cursor.fetchone()

            if not returned_info or (not user.code==returned_info["login"]):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invalid credes",
                )# removed hash check for now
            role = returned_info["role"]
            returned_info["role"] = [role]
            id = returned_info["id"]
            recentAmendments = asyncio.create_task(getRecentAmendments()) 
            del returned_info["login"]
            returned_info.update({"accessToken": generateJwt(returned_info, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES)})
            response.set_cookie(key="refresh_token",value=f"Bearer {generateJwt(returned_info, REFRESH_KEY, REFRESH_TOKEN_EXPIRE_MINUTES)}", httponly=True, secure=False, samesite="lax", path="/refresh")
            if roleList.get("member") in returned_info["role"]:
                personalDetails = asyncio.create_task(personalProfile(id))
                ownAmendments = asyncio.create_task(getOwnAmendments(id))

                print(personalDetails)
                returned_info["personalDetails"] = await personalDetails
                returned_info["ownAmendments"] = await ownAmendments
                returned_info["recentAmendments"] = await recentAmendments
            elif role == roleList.get("admin"):
                personalDetails = await specificProfile(id)
                await recentAmendments
                returned_info["personalDetails"] = await personalDetails
                returned_info["recentAmendments"] = await recentAmendments
            print(returned_info)
            return returned_info # set secure cookie once not in dev
    

@router.post("/logout")
def logout(response: Response, request: Request, status_code=status.HTTP_200_OK):
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
    token = token.replace("Bearer ", "")
    payload = await decode(token, REFRESH_KEY)
    if token:
        recentAmendments = asyncio.create_task(getRecentAmendments()) # wraps a async coroutine object into a task
        # create task is used so that getResolutions() is run right here in the background and we await retrieve the result later
        # this allows for the rest of the function to run while the task is being executed
        newAccess = generateJwt(payload, REFRESH_KEY, REFRESH_TOKEN_EXPIRE_MINUTES)
        if payload.get("role") == roleList.get("member"):
            personalDetails = asyncio.create_task(personalProfile(payload["id"]))
            ownAmendments = asyncio.create_task(getOwnAmendments(payload["id"]))
            return {"accessToken": newAccess, "role": payload["role"], "country": payload["country"], "id": payload["id"], "personalDetails": await personalDetails, "ownAmendments": await ownAmendments, "recentAmendments": await recentAmendments}
        elif payload.get("role") == roleList.get("admin"):
            personalDetails = await specificProfile(payload["id"])
        return {"accessToken": newAccess, "role": payload["role"], "country": payload["country"], "personalDetails": personalDetails, "recentAmendments": await recentAmendments}
    else:
        raise HTTPException(status_code=401, detail="Missing refresh token")

# general page, return the personal profile of the country, own amendments, recent amendments added
# general amendments page
# general resolutions page
# general general countries page

# admin dashboard, return all resolutions general, amendments general, countries general 