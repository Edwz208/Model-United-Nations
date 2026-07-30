# app/modules/auth/router.py

from fastapi import APIRouter, status, Response, Cookie, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Any
from app.core.database import get_db
from app.modules.auth.repository import AuthRepository
from app.modules.auth.service import AuthService
from app.modules.auth.schemas import LoginIn

router = APIRouter(prefix="/auth", tags=["auth"])

def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(AuthRepository(session))

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user: LoginIn, response: Response, service: AuthService = Depends(get_auth_service)) -> dict[str, Any]:
    returned_info = await service.login(user.country, user.code, response)
    return returned_info

@router.post("/logout")
def logout(response: Response) -> dict[str, Any]:
    response.delete_cookie(key="refresh_token", httponly=True, secure=False, samesite="lax", path="/refresh")
    return {"message": "success", "accessToken": ""}

@router.get("/refresh")
async def refresh_access_token(refresh_token: Annotated[str | None, Cookie()] = None, service: AuthService = Depends(get_auth_service)) -> dict[str, Any] | None:
    result = await service.refresh_login(refresh_token)
    return result
