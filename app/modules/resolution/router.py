# app/modules/resolution/router.py

from fastapi import APIRouter, status, UploadFile, File, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Optional
from app.core.dependencies import require_admin, require_member_or_admin
from app.core.database import get_db
from app.modules.resolution.repository import ResolutionRepository
from app.modules.resolution.service import ResolutionService
from app.modules.resolution.schemas import SelectResolutionsToDelete, ResolutionListOut, ResolutionDetailOut

router = APIRouter(prefix="/resolutions", tags=["resolutions"])

def get_resolution_service(session: AsyncSession = Depends(get_db)) -> ResolutionService:
    return ResolutionService(ResolutionRepository(session))

@router.get("", status_code=status.HTTP_200_OK)
async def list_resolutions(current_user=Depends(require_member_or_admin), service: ResolutionService = Depends(get_resolution_service)) -> list[ResolutionListOut]:
    return await service.get_all_resolutions_general_info()

@router.get('/council/{council_id}', status_code=status.HTTP_200_OK)
async def list_council_resolutions(council_id: int, current_user=Depends(require_member_or_admin), service: ResolutionService = Depends(get_resolution_service)) -> list[ResolutionListOut]:
    return await service.get_all_council_resolutions_general_info(council_id)

@router.get('/{resolution_id}', status_code=status.HTTP_200_OK)
async def get_resolution(resolution_id: int, current_user=Depends(require_member_or_admin), service: ResolutionService = Depends(get_resolution_service)) -> ResolutionDetailOut:
    return await service.get_specific_resolution(resolution_id)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_resolution(
    council_id: int = Form(...),
    title: str = Form(...),
    number: int = Form(...),
    clauses: int = Form(...),
    submitter: int = Form(...),
    seconder: int = Form(...),
    negator: int = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(require_admin),
    service: ResolutionService = Depends(get_resolution_service)
) -> dict[str, Any]:
    resolution = await service.upload_resolution(council_id, title, number, clauses, submitter, seconder, negator, file)
    return {"message": "success", "resolution": resolution}

@router.delete("", status_code=status.HTTP_200_OK)
async def delete_resolutions(resolutions: SelectResolutionsToDelete, current_user=Depends(require_admin), service: ResolutionService = Depends(get_resolution_service)) -> dict[str, Any]:
    result = await service.delete_resolutions(resolutions.resolution_ids)
    return {"message": "success", "resolution": result}

@router.patch('/{resolution_id}', status_code=status.HTTP_200_OK)
async def update_resolution(resolution_id: int, current_user=Depends(require_admin), council_id: Optional[int] = Form(None), title: Optional[str] = Form(None), clauses: Optional[int] = Form(None), submitter: Optional[int] = Form(None), seconder: Optional[int] = Form(None), negator: Optional[int] = Form(None), res_status: Optional[str] = Form(None), number: Optional[int] = Form(None), file: UploadFile = File(None), service: ResolutionService = Depends(get_resolution_service)) -> dict[str, Any]:
    result = await service.update_resolution(title, council_id, res_status, clauses, submitter, seconder, negator, number, file, resolution_id)
    return {"message": "success", "resolution": result}
