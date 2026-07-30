# app/core/security.py

from passlib.context import CryptContext
import asyncio
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from app.core.settings import get_settings
from app.core.exceptions import AuthorizationException

settings = get_settings()

REFRESH_KEY = settings.REFRESH_KEY
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES

SECRET_KEY = settings.SECRET_KEY
if not SECRET_KEY:
    SECRET_KEY = "TEST_SECRET"


async def hash(password: str) -> str:
    return await asyncio.to_thread(pwd_context.hash, password)

async def verify(plain: str, hashed: str) -> bool:
        return await asyncio.to_thread(pwd_context.verify, plain, hashed)

async def decode(token: str, key: str) -> dict: 
    try:
        return await asyncio.to_thread(jwt.decode, token, key, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise AuthorizationException("Invalid token")

def generate_access_token(data: dict, KEY: str, time_minutes: float) -> str:
    to_encode = data.copy() # must generate copy becausue dict is mutable
    expire = datetime.now(timezone.utc) + timedelta(minutes=time_minutes)
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, KEY, algorithm=ALGORITHM)
    return encoded_jwt