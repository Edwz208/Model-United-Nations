from fastapi import APIRouter, HTTPException, status, Depends
from schemas import Exec, ExecPatch
from helpers import require_admin, fetch_all, fetch_one
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()

@router.post("/set-exec", status_code = status.HTTP_200_OK)
async def setExec(person: Exec, current_user=Depends(require_admin)):
    execSet = await fetch_one('''INSERT INTO secretariat (name, position) VALUES (%s,%s) RETURNING *;''', (person.name, person.position))
    return {"status": "success", **execSet}
        
@router.get("/get-secretariat", status_code = status.HTTP_200_OK)
async def getAllExecs():
    allExecs = await fetch_all("""SELECT name, position, secretariat_id from secretariat""") or []
    return allExecs
        
@router.delete('/delete-secretariat/{secretariat_id}', status_code = status.HTTP_200_OK)
async def deleteExec(secretariat_id: int, current_user=Depends(require_admin)):
    result = await fetch_one('''DELETE FROM secretariat WHERE secretariat_id = %s RETURNING name, position, secretariat_id''', (secretariat_id,))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Secretariat not found",
        )
    return {"status": "success", **result}
    
@router.patch('/update-secretariat/{secretariat_id}', status_code = status.HTTP_200_OK)
async def updateExec(exec: ExecPatch, id: int, current_user=Depends(require_admin)):
    result = await fetch_one('''UPDATE secretariat SET name = COALESCE(%s, name), position = COALESCE(%s, position) WHERE secretariat_id = %s RETURNING *''', (exec.name, exec.position, id,))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Secretariat not found",
        )
    return {"status": "success", **result}
