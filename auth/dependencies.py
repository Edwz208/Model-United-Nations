from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from config import settings
from auth.json_web_token import decode
from typing import Any

async def get_current_user(token: str) -> dict[str, Any]:
    payload = await decode(token, settings.SECRET_KEY)
    return payload

async def require_admin(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    payload = await get_current_user(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return payload

async def require_member_or_admin(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    payload = await get_current_user(token)
    if payload.get("role") not in ["admin", "member"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return payload

async def require_specific_member_or_admin(country_id: int, token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    payload = await get_current_user(token)
    if payload.get("role") != "admin" and payload.get("id") != country_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return payload