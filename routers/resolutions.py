from fastapi import APIRouter, status, UploadFile, File, Form, Depends
from services.resolutions import update_resolution_service, upload_resolution_service, get_all_resolutions_general_info_service, get_all_council_resolutions_general_info_service, get_specific_resolution_service, delete_resolution_service
from auth.dependencies import require_admin, require_member_or_admin
from typing import Any, Optional

# For resolutions, we allow admin to change the order of resolutions, change the order of multiple at once after saving to make it one call to the server
router = APIRouter()

@router.get('/get-all-resolutions-general-info', status_code=status.HTTP_200_OK)
async def get_all_resolutions_general_info(current_user=Depends(require_member_or_admin)) -> list[dict[str, Any]]:
    result = await get_all_resolutions_general_info_service()
    return result

@router.get('/get-all-resolutions-general-info/{council_id}', status_code=status.HTTP_200_OK)
async def get_council_all_resolutions_general_info(council_id: int, current_user=Depends(require_member_or_admin)) -> list[dict[str, Any]]:
    result = await get_all_council_resolutions_general_info_service(council_id)
    return result

@router.get('/get-resolution/{resolution_id}}', status_code=status.HTTP_200_OK)
async def specific_resolution(resolution_id: int, current_user=Depends(require_member_or_admin)):
    resolution = await get_specific_resolution_service(resolution_id)
    return resolution

@router.post('/upload-resolution',status_code = status.HTTP_200_OK)
async def uploading_resolution(#put non default arguments before default arguments Depends is non deafult
    council_id: int = Form(...),
    title: str = Form(...),
    clauses: int = Form(...),
    submitter: int = Form(...),
    seconder: int = Form(...),
    negator: int = Form(...),
    file: UploadFile = File(...),
    current_user = Depends(require_admin)
    # missing status, amendment_count
) -> dict[str, Any]:
    resolution = await upload_resolution_service(council_id, title, clauses, submitter, seconder, negator, file)
    return {"message": "success", **resolution}
    

@router.delete('/delete-resolution/{resolution_id}', status_code=status.HTTP_200_OK)
async def delete_resolution(resolution_id: int, current_user=Depends(require_admin)) -> dict[str, Any]:
    result = await delete_resolution_service(resolution_id)   
    return {"message":"success", **result}
    
@router.patch('/update-resolution/{resolution_id}',status_code=status.HTTP_200_OK)
async def update_resolution(resolution_id: int, current_user=Depends(require_admin), council_id: Optional[int] = Form(None), title: Optional[str] = Form(None), clauses: Optional[int] = Form(None), submitter: Optional[int] = Form(None), seconder: Optional[int] = Form(None), negator: Optional[int] = Form(None), res_status: Optional[str] = Form(None), number: Optional[int] = Form(None), file: UploadFile = File(None)) -> dict[str, Any]:
    result = await update_resolution_service(title, council_id, res_status, clauses, submitter, seconder, negator, number, file, resolution_id)
    return {"message": "success", **result}