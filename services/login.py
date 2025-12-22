from fastapi import HTTPException, status, Response
from db.utils import fetch_one
from auth.json_web_token import generateJwt, decode
from config import settings
from typing import Any

async def login_service(country: str, code: str, response: Response) -> dict[str, Any]:
    returned_info = await fetch_one("""SELECT login, name, country_id, role from countries WHERE name = %s""", (country.lower().capitalize(),))
    if not returned_info or (not code == returned_info["login"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credes",
        ) # removed hash check for now
        
    del returned_info["login"]
    returned_info.update({"accessToken": generateJwt(returned_info, settings.SECRET_KEY, settings.ACCESS_TOKEN_EXPIRE_MINUTES)})
    response.set_cookie(key="refresh_token",value=generateJwt(returned_info, settings.REFRESH_KEY, settings.REFRESH_TOKEN_EXPIRE_MINUTES), httponly=True, secure=False, samesite="lax", path="/refresh")
    return returned_info
    # set secure cookie once not in dev

async def refresh_login_service(refresh_token: str | None) -> dict[str, Any] | None:
    print(f"Refresh token from cookies: {refresh_token}")
    if refresh_token:
        payload = await decode(refresh_token, settings.REFRESH_KEY)
        newAccess = generateJwt(payload, settings.SECRET_KEY, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {"message": "success", "accessToken": newAccess, "role": payload["role"], "name": payload["name"], "country_id": payload["country_id"]}
    else:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    