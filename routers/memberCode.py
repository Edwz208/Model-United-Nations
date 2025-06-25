from fastapi import APIRouter
from authentication import verify
from schemas import User

router = APIRouter()

@router.post("/login")
async def login(user: User): 
        return {"username": user.code, "role": "member"}