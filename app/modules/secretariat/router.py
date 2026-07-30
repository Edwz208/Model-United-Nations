# app/modules/secretariat/router.py

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from app.core.dependencies import require_admin
from app.core.database import get_db
from app.modules.secretariat.repository import SecretariatRepository
from app.modules.secretariat.service import SecretariatService
from app.modules.secretariat.schemas import ExecIn, ExecPatch, SecretariatOut

router = APIRouter(prefix="/secretariat", tags=["secretariat"])

def get_secretariat_service(session: AsyncSession = Depends(get_db)) -> SecretariatService:
    return SecretariatService(SecretariatRepository(session))

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_exec(person: ExecIn, current_user=Depends(require_admin), service: SecretariatService = Depends(get_secretariat_service)) -> dict[str, Any]:
    execSet = await service.post_exec(person.name, person.position)
    return {"message": "success", "exec": execSet}

@router.get("", status_code=status.HTTP_200_OK)
async def list_execs(service: SecretariatService = Depends(get_secretariat_service)) -> list[SecretariatOut]:
    return await service.get_all_execs()

@router.delete('/{secretariat_id}', status_code=status.HTTP_200_OK)
async def delete_exec(secretariat_id: int, current_user=Depends(require_admin), service: SecretariatService = Depends(get_secretariat_service)) -> dict[str, Any]:
    result = await service.delete_exec(secretariat_id)
    return {"message": "success", "exec": result}

@router.patch('/{secretariat_id}', status_code=status.HTTP_200_OK)
async def update_exec(exec: ExecPatch, secretariat_id: int, current_user=Depends(require_admin), service: SecretariatService = Depends(get_secretariat_service)) -> dict[str, Any]:
    result = await service.update_exec(exec.name, exec.position, secretariat_id)
    return {"message": "success", "exec": result}
