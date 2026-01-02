from fastapi import APIRouter, status, Depends
from schemas import Exec, ExecPatch
from auth.dependencies import require_admin
from services.secretariat import post_exec_service, delete_exec_service, update_exec_service
from typing import Any
from db.utils import fetch_all
router = APIRouter()

@router.post("/set-exec", status_code = status.HTTP_200_OK)
async def set_exec(person: Exec, current_user=Depends(require_admin)) -> dict[str, Any]:
    execSet = await post_exec_service(person.name, person.position)
    return {"message": "success", "exec": execSet}
        
@router.get("/get-secretariat", status_code = status.HTTP_200_OK)
async def get_all_execs() -> list[dict[str, Any]]:
    allExecs = await fetch_all('''SELECT name, position, secretariat_id from secretariat''')
    return allExecs
        
@router.delete('/delete-secretariat/{secretariat_id}', status_code = status.HTTP_200_OK)
async def delete_exec(secretariat_id: int, current_user=Depends(require_admin)) -> dict[str, Any]:
    result = await delete_exec_service(secretariat_id)
    return {"message": "success", "exec": result}
    
@router.patch('/update-secretariat/{secretariat_id}', status_code = status.HTTP_200_OK)
async def update_exec(exec: ExecPatch, secretariat_id: int, current_user=Depends(require_admin)) -> dict[str, Any]:
    result = await update_exec_service(exec.name, exec.position, secretariat_id)
    return {"message": "success", "exec": result}
