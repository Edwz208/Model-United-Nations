from fastapi import APIRouter, HTTPException, status, Depends
from schemas import Exec, ExecPatch
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from helpers import require_admin, fetch_all, fetch_one

router = APIRouter()

@router.post("/set-exec", status_code = status.HTTP_200_OK)
async def setExec(person: Exec, current_user=Depends(require_admin)):
    return await fetch_one('''INSERT INTO secretariat (name, position) VALUES (%s,%s) ON CONFLICT (name)
                        DO UPDATE SET name = EXCLUDED.name, position = EXCLUDED.position RETURNING *;''',
                        (person.name, person.position))
        
@router.get("/get-secretariat", status_code = status.HTTP_200_OK)
async def getAllExecs():
    return await fetch_all("""SELECT name, position, secretariat_id from secretariat""")
        
@router.delete('/delete-secretariat/{id}', status_code = status.HTTP_200_OK)
async def deleteExec(id: str, current_user=Depends(require_admin)):
    result = await fetch_one('''delete from secretariat where secretariat_id = %s returning *''', (id,))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Name not found",
        )
    return result
    
@router.patch('/update-secretariat/{id}', status_code = status.HTTP_200_OK)
async def updateExec(exec: ExecPatch, id: int, current_user=Depends(require_admin)):
    result = await fetch_one('''UPDATE secretariat SET 
                                    name = COALESCE(%s, name),
                                    position = COALESCE(%s, position) WHERE secretariat_id = %s RETURNING *''', (exec.name, exec.position, id,))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Name not found",
        )
    return result