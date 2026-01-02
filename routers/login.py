from fastapi import APIRouter, status, Response, Cookie
from schemas import User
from typing import Annotated, Any
from services.login import login_service, refresh_login_service
router = APIRouter()

@router.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def login(user: User, response: Response) -> dict[str, Any]:
    returned_info = await login_service(user.country, user.code, response)
    return returned_info

@router.post("/logout")
def logout(response: Response) -> dict[str, Any]:
    response.delete_cookie(key="refresh_token", httponly=True, secure=False, samesite="lax", path="/refresh")       
    print("cookie deleted")
    return {"message": "success", "accessToken": ""}

@router.get("/refresh")
async def refresh_token(refresh_token: Annotated[str | None, Cookie()] = None) -> dict[str, Any] | None: # unlike depends does not call a function but tells fastapi where to get value from
    result = await refresh_login_service(refresh_token)
    return result