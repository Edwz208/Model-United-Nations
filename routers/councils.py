from fastapi import APIRouter, status, Depends
from schemas import Council, CouncilPatch
from auth.dependencies import require_member_or_admin, require_admin
from typing import Any
router = APIRouter()
from backend.services.councils import get_all_councils_service, post_council_service, delete_council_service, update_council_service, update_main_council_service

@router.get('/get-councils-list', status_code=status.HTTP_200_OK)
async def all_councils(current_user=Depends(require_member_or_admin)) -> list[dict[str, Any]]:
    councils = await get_all_councils_service()
    return councils

@router.post("/set-council", status_code = status.HTTP_200_OK)
async def add_council(council: Council, current_user=Depends(require_admin)) -> dict[str, Any]:
    councilSet = await post_council_service(council.name, council.resolution_count)
    return {"message": "success", **councilSet}
        
@router.delete('/delete-council/{council_id}', status_code = status.HTTP_200_OK)
async def delete_council(council_id: int, current_user=Depends(require_admin)) -> dict[str, Any]:
    result = await delete_council_service(council_id)
    return {"message": "success", **result}
    
@router.patch('/update-council/{council_id}', status_code = status.HTTP_200_OK)
async def update_council(council: CouncilPatch, council_id: int, current_user=Depends(require_admin)) -> dict[str, Any]:
    result = await update_council_service(council.name, council.resolution_count, council_id)
    return {"message": "success", **result}

@router.patch('/update-main-council/{council_id}', status_code=status.HTTP_200_OK)
async def update_main_council(council_id: int, current_user=Depends(require_admin)) -> dict[str, Any]:
    result = await update_main_council_service(council_id)
    return {"message": "success", **result}