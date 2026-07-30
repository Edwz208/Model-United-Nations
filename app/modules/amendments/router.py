# app/modules/amendments/router.py

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from app.core.dependencies import require_member_or_admin, require_specific_member_or_admin, require_admin
from app.core.database import get_db
from app.modules.amendments.repository import AmendmentRepository
from app.modules.amendments.service import AmendmentService
from app.modules.amendments.schemas import AmendmentIn, AmendmentPatch, ApproveRejectAmendment, AmendmentOut

router = APIRouter(prefix="/amendments", tags=["amendments"])

def get_amendment_service(session: AsyncSession = Depends(get_db)) -> AmendmentService:
    return AmendmentService(AmendmentRepository(session))

@router.get('/country/{country_id}', status_code=status.HTTP_200_OK)
async def get_country_amendments(country_id: int, current_user=Depends(require_specific_member_or_admin), service: AmendmentService = Depends(get_amendment_service)) -> list[AmendmentOut]:
    return await service.get_own_amendments(country_id)

@router.get('/resolution/{resolution_id}', status_code=status.HTTP_200_OK)
async def list_resolution_amendments(resolution_id: int, current_user=Depends(require_member_or_admin), service: AmendmentService = Depends(get_amendment_service)) -> list[AmendmentOut]:
    return await service.get_all_amendments_for_resolution(resolution_id)

@router.get('/council/{council_id}', status_code=status.HTTP_200_OK)
async def list_council_amendments(council_id: int, current_user=Depends(require_member_or_admin), service: AmendmentService = Depends(get_amendment_service)) -> list[AmendmentOut]:
    return await service.get_all_amendments_for_council(council_id)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_amendment(amendment: AmendmentIn, current_user=Depends(require_member_or_admin), service: AmendmentService = Depends(get_amendment_service)) -> AmendmentOut:
    return await service.upload_amendment(amendment.content, amendment.clause, amendment.resolution_id, amendment.submitter, amendment.status)

@router.patch('/{amendment_id}/country/{country_id}')
async def update_amendment(amendment_id: int, country_id: int, amendment: AmendmentPatch, current_user=Depends(require_specific_member_or_admin), service: AmendmentService = Depends(get_amendment_service)) -> AmendmentOut:
    return await service.update_amendment(amendment_id, amendment.resolution_id, amendment.status, amendment.submitter, amendment.clause, amendment.content)

@router.delete('/{amendment_id}', status_code=status.HTTP_200_OK)
async def delete_amendment(amendment_id: int, current_user=Depends(require_member_or_admin), service: AmendmentService = Depends(get_amendment_service)) -> dict[str, Any]:
    result = await service.delete_amendment(amendment_id)
    return {"message": "success", "amendment": result}

@router.patch('/{amendment_id}/review', status_code=status.HTTP_200_OK)
async def review_amendment(amendment_id: int, approve_reject: ApproveRejectAmendment, current_user=Depends(require_admin), service: AmendmentService = Depends(get_amendment_service)) -> dict[str, Any]:
    result = await service.approve_reject_amendment(amendment_id, approve_reject.status, approve_reject.reject_message)
    return {"message": "success", "amendment": result}
