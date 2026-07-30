# app/modules/councils/router.py

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from app.core.dependencies import require_member_or_admin, require_admin
from app.core.database import get_db
from app.modules.councils.repository import CouncilRepository
from app.modules.councils.service import CouncilService
from app.modules.councils.schemas import CouncilIn, CouncilPatch, CouncilOut

router = APIRouter(prefix="/councils", tags=["councils"])

def get_council_service(session: AsyncSession = Depends(get_db)) -> CouncilService:
    return CouncilService(CouncilRepository(session))

@router.get("", status_code=status.HTTP_200_OK)
async def list_councils(current_user=Depends(require_member_or_admin), service: CouncilService = Depends(get_council_service)) -> list[CouncilOut]:
    return await service.get_all_councils()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_council(council: CouncilIn, current_user=Depends(require_admin), service: CouncilService = Depends(get_council_service)) -> dict[str, Any]:
    councilSet = await service.post_council(council.name, council.resolution_count)
    return {"message": "success", "council": councilSet}

@router.delete('/{council_id}', status_code=status.HTTP_200_OK)
async def delete_council(council_id: int, current_user=Depends(require_admin), service: CouncilService = Depends(get_council_service)) -> dict[str, Any]:
    result = await service.delete_council(council_id)
    return {"message": "success", "council": result}

@router.patch('/{council_id}', status_code=status.HTTP_200_OK)
async def update_council(council: CouncilPatch, council_id: int, current_user=Depends(require_admin), service: CouncilService = Depends(get_council_service)) -> dict[str, Any]:
    result = await service.update_council(council.name, council.resolution_count, council_id)
    return {"message": "success", "council": result}

@router.patch('/{council_id}/main', status_code=status.HTTP_200_OK)
async def update_main_council(council_id: int, current_user=Depends(require_admin), service: CouncilService = Depends(get_council_service)) -> dict[str, Any]:
    result = await service.update_main_council(council_id)
    return {"message": "success", "council": result}
