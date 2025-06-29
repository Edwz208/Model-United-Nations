from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

async def hash(password: str):
    return pwd_context.hash(password)

async def verify(plain, hashed):
    return pwd_context.verify(plain, hashed)
