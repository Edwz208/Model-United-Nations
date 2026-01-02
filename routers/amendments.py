from fastapi import APIRouter, status, Depends
from auth.dependencies import require_member_or_admin, require_specific_member_or_admin, require_admin
from schemas import Amendment, AmendmentPatch, ApproveRejectAmendment
from typing import Any
from services.amendments import get_own_amendments_service, get_all_amendments_for_resolution_service, approve_reject_amendment_service, update_amendment_service, delete_amendment_service, upload_amendment_service
router = APIRouter()
        
@router.get('/specific-amendment-country/{country_id}', status_code=status.HTTP_200_OK)
async def specific_country_amendments(country_id: int, current_user=Depends(require_specific_member_or_admin)) -> list[dict[str, Any]]:
    amendments = await get_own_amendments_service(country_id)
    return amendments

@router.get('/all-amendments/{resolution_id}', status_code=status.HTTP_200_OK)
async def all_amendments_for_resolution(resolution_id: int, current_user=Depends(require_member_or_admin)) -> list[dict[str, Any]]:
    result = await get_all_amendments_for_resolution_service(resolution_id)
    return result

@router.post('/upload-amendment',status_code = status.HTTP_200_OK)
async def uploading_amendment(amendment: Amendment, current_user=Depends(require_member_or_admin)):
    result = await upload_amendment_service(amendment.content, amendment.clause, amendment.resolution_id, amendment.submitter, amendment.status)
    return result

@router.patch('/update-amendment/{amendment_id}/{country_id}')
async def update_amendment(amendment_id: int, country_id: int, amendment: AmendmentPatch, current_user=Depends(require_specific_member_or_admin)) -> dict[str, Any]:
    result = await update_amendment_service(amendment_id, amendment.resolution_id, amendment.status, amendment.submitter, amendment.clause, amendment.content)
    return result
        
@router.delete('/delete-amendment/{amendment_id}', status_code=status.HTTP_200_OK)
async def delete_amendment(amendment_id: int, current_user=Depends(require_member_or_admin)) -> dict[str, Any]:
    result = await delete_amendment_service(amendment_id)
    return {"message": "success", "amendment": result}

@router.post('/approve-reject-amendment/{amendment_id}', status_code=status.HTTP_200_OK)
async def approve_reject_amendment(amendment_id: int, approve_reject: ApproveRejectAmendment, current_user=Depends(require_admin)) -> dict[str, Any]:
    result = await approve_reject_amendment_service(amendment_id, approve_reject.status, approve_reject.reject_message)
    return {"message": "success", "amendment": result}