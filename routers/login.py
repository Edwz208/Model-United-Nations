from fastapi import APIRouter, status, HTTPException, Response, Cookie
from authentication import decode, generateJwt, SECRET_KEY, REFRESH_KEY, REFRESH_TOKEN_EXPIRE_MINUTES, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import User
router = APIRouter()
from helpers import fetch_one
from typing import Annotated


@router.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def login(user: User, response: Response) -> dict:
        returned_info = await fetch_one("""SELECT login, name, country_id, role from countries WHERE name = %s""", (user.country.lower().capitalize(),))
        if not returned_info or (not user.code == returned_info["login"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credes",
            ) # removed hash check for now
        
        del returned_info["login"]
        returned_info.update({"accessToken": generateJwt(returned_info, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES)})
        response.set_cookie(key="refresh_token",value=generateJwt(returned_info, REFRESH_KEY, REFRESH_TOKEN_EXPIRE_MINUTES), httponly=True, secure=False, samesite="lax", path="/refresh")
        return {"status": "success", **returned_info} # set secure cookie once not in dev
    

@router.post("/logout")
def logout(response: Response) -> dict:
    response.delete_cookie(key="refresh_token", httponly=True, secure=False, samesite="lax", path="/refresh")       
    print("cookie deleted")
    return {"status": "success", "accessToken": ""}


@router.get("/refresh")
async def refresh_token(refresh_token: Annotated[str | None, Cookie()] = None) -> dict:
    print(f"Refresh token from cookies: {refresh_token}")
    if refresh_token:
        payload = await decode(refresh_token, REFRESH_KEY)
        newAccess = generateJwt(payload, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES)
        return {"status": "success", "accessToken": newAccess, "role": payload["role"], "name": payload["name"], "country_id": payload["country_id"]}
    else:
        raise HTTPException(status_code=401, detail="Missing refresh token")