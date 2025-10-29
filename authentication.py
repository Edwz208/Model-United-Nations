from passlib.context import CryptContext
import asyncio
import jwt
from jwt.exceptions import InvalidTokenError
import os
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status

roleList = {
  "member": "2007",
  "admin": "4015"
}

SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_KEY = os.getenv("REFRESH_KEY")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 10080 # 7 days


async def hash(password: str) -> str:
    return await asyncio.to_thread(pwd_context.hash, password)

async def verify(plain: str, hashed: str) -> bool:
        return await asyncio.to_thread(pwd_context.verify, plain, hashed)

async def decode(token: str, key: str) -> dict: 
    try:
        return await asyncio.to_thread(jwt.decode, token, key, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def generateJwt(data: dict, KEY: str, time_minutes: float) -> str:
    to_encode = data.copy() # must generate copy becausue dict is mutable
    expire = datetime.now(timezone.utc) + timedelta(minutes=time_minutes)
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("id") 
        if id is None:
            raise credentials_exception
        else: 
            return payload
    except InvalidTokenError: 
        raise credentials_exception
    
        

        
