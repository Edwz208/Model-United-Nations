# app/modules/auth/service.py

from fastapi import Response
from app.modules.auth.repository import AuthRepository
from app.core.settings import get_settings
from app.core.security import decode, generate_access_token
from app.core.exceptions import InvalidCredentialsException, RefreshTokenMissingException

settings = get_settings()

class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    async def login(self, country: str, code: str, response: Response) -> dict:
        entity = await self.repository.get_by_name(country.lower().capitalize())
        if not entity or code != entity.login:
            raise InvalidCredentialsException()

        payload = {"name": entity.name, "country_id": entity.country_id, "role": entity.role}
        access_token = generate_access_token(payload, settings.SECRET_KEY, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token = generate_access_token(payload, settings.REFRESH_KEY, settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", path="/refresh", max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60)
        payload.update({"accessToken": access_token})
        return payload

    async def refresh_login(self, refresh_token: str | None) -> dict:
        if not refresh_token:
            raise RefreshTokenMissingException()
        payload = await decode(refresh_token, settings.REFRESH_KEY)
        new_access = generate_access_token(payload, settings.SECRET_KEY, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {"message": "success", "accessToken": new_access, "role": payload.get("role"), "name": payload.get("name"), "country_id": payload.get("country_id")}
