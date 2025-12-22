from fastapi import APIRouter, HTTPException, status, Depends
from schemas import Exec, ExecPatch
from helpers import require_admin, fetch_all, fetch_one

router = APIRouter()

@router.post("/set-exec", status_code = status.HTTP_200_OK)
async def setExec(person: Exec, current_user=Depends(require_admin)):
    execSet = await fetch_one('''INSERT INTO secretariat (name, position) VALUES (%s,%s) RETURNING name, position, secretariat_id;''', (person.name, person.position))
    return {"message": "success", **execSet}
        
@router.get("/get-secretariat", status_code = status.HTTP_200_OK)
async def getAllExecs():
    allExecs = await fetch_all('''SELECT name, position, secretariat_id from secretariat''')
    return allExecs
        
@router.delete('/delete-secretariat/{secretariat_id}', status_code = status.HTTP_200_OK)
async def deleteExec(secretariat_id: int, current_user=Depends(require_admin)):
    result = await fetch_one('''DELETE FROM secretariat WHERE secretariat_id = %s RETURNING name, position, secretariat_id''', (secretariat_id,))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Secretariat not found",
        )
    return {"message": "success", **result}
    
@router.patch('/update-secretariat/{secretariat_id}', status_code = status.HTTP_200_OK)
async def updateExec(exec: ExecPatch, secretariat_id: int, current_user=Depends(require_admin)):
    result = await fetch_one('''UPDATE secretariat SET name = COALESCE(%s, name), position = COALESCE(%s, position) WHERE secretariat_id = %s RETURNING *''', (exec.name, exec.position, secretariat_id,))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Secretariat not found",
        )
    return {"message": "success", **result}
