from passlib.context import CryptContext
import asyncio
import jwt
from jwt.exceptions import InvalidTokenError
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from typing import Annotated
load_dotenv()
from fastapi import Depends, FastAPI, HTTPException, status

roleList = {
  "member": 2007,
  "admin": 4015
}

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def hash(password: str):
    return await asyncio.to_thread(pwd_context.hash, password)

async def verify(plain: str, hashed: str):
        return await asyncio.to_thread(pwd_context.verify, plain, hashed)

def generateJwt(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
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
    
        