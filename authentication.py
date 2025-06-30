from passlib.context import CryptContext
import asyncio

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

async def hash(password: str):
    return await asyncio.to_thread(pwd_context.hash, password)

async def verify(plain: str, hashed: str):
        return await asyncio.to_thread(pwd_context.verify, plain, hashed)
