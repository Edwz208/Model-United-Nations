from passlib.context import CryptContext
import asyncio
import jwt
from jwt.exceptions import InvalidTokenError
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from typing import Annotated
load_dotenv()
from fastapi import Depends, APIRouter, HTTPException, status, Response, Request
from psycopg.rows import dict_row
from db import get_async_pool


pool = get_async_pool()

roleList = {
  "member": 2007,
  "admin": 4015
}

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_KEY = os.getenv("REFRESH_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def hash(password: str):
    return await asyncio.to_thread(pwd_context.hash, password)

async def verify(plain: str, hashed: str):
        return await asyncio.to_thread(pwd_context.verify, plain, hashed)

def generateJwt(data: dict, response: Response):
    to_encode = data.copy()
    to_encodeR = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    expireR = datetime.now(timezone.utc) + timedelta(days=7)
    to_encodeR.update({"exp": expireR})
    refresh_jwt = jwt.encode(to_encodeR, REFRESH_KEY, algorithm=ALGORITHM)
    response.set_cookie(key="refresh_token",value=f"Bearer {refresh_jwt}", httponly=True, secure=True, samesite="lax")
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
    
router = APIRouter()
adminPaths = ["countries, resolutions, amendments, projection-dashboard"]

async def getCountryNames():
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute("""SELECT country from delegates""")
            allCount = await cursor.fetchall()
            return allCount
        
        
async def getResolutions():
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute('''SELECT number, title, clauses, council_id, submitter, seconder, negator, url from resolutions''')
            allResolutions = await cursor.fetchall()
            return allResolutions
        
@router.get("/refresh")
async def refresh_token(request: Request, pathName = str ):
    token = request.cookies.get("refresh_token")
    if token:
        task = asyncio.create_task(getResolutions())
        task1 = asyncio.create_task(getCountryNames())
        token = token.replace("Bearer ", "")
        payload = jwt.decode(token, REFRESH_KEY, algorithms=[ALGORITHM])
        payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=15)
        newAccess = jwt.encode(payload, SECRET_KEY, algorithm = ALGORITHM)
        await task
        await task1
        return {"accessToken": newAccess, "role": payload["role"], "country": payload["country"], "countryNames": task1, "resolutions": task}
    else:
        raise HTTPException(status_code=401, detail="Missing access token")
    
    # for sure need country names 
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="refresh_token", httponly=True)
    return {"message": "Logged out"}
        