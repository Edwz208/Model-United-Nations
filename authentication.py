from passlib.context import CryptContext
import asyncio
import jwt
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv
load_dotenv()
import os
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Response

roleList = {
  "member": "2007",
  "admin": "4015"
}
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_KEY = os.getenv("REFRESH_KEY")
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 10080 # 7 days


async def hash(password: str):
    return await asyncio.to_thread(pwd_context.hash, password)

async def verify(plain: str, hashed: str):
        return await asyncio.to_thread(pwd_context.verify, plain, hashed)

async def decode(token: str, key: str):
    try:
        return await asyncio.to_thread(jwt.decode, token, key, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def generateJwt(data: dict, KEY,time_minutes: float):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=time_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        country = payload.get("country")
        if country is None:
            raise credentials_exception
        else: 
            return payload
    except InvalidTokenError: 
        raise credentials_exception
    
        

        