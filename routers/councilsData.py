from fastapi import APIRouter, HTTPException, status, Depends
from schemas import Council, CouncilPatch
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from helpers import require_member_or_admin, require_admin, fetch_all, fetch_one, transaction, execute
router = APIRouter()

async def getCouncilsList() -> list[dict]:
    allCouncils = await fetch_all('''SELECT council_id, name, resolution_count from councils''') or []
    return allCouncils

async def returnMainCouncil() -> dict:
    mainCouncil = await fetch_one('''SELECT council_id, name, resolution_count from councils WHERE is_main = TRUE''')
    return mainCouncil

@router.get('/get-councils-list', status_code=status.HTTP_200_OK)
async def genResolutionsRoute(current_user=Depends(require_member_or_admin)):
    resolutions = await getCouncilsList()
    return resolutions

@router.post("/set-council", status_code = status.HTTP_200_OK)
async def setCouncil(council: Council, current_user=Depends(require_admin)):
    councilSet = await fetch_one('''INSERT INTO secretariat (name, resolution_count) VALUES (%s,%s) RETURNING *;''', (council.name, council.resolution_count))
    return {"status": "success", **councilSet}
        
@router.delete('/delete-council/{council_id}', status_code = status.HTTP_200_OK)
async def deleteCouncil(council_id: int, current_user=Depends(require_admin)):
    result = await fetch_one('''DELETE FROM council WHERE council_id = %s RETURNING name, resolution_count, council_id''', (council_id,))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Council not found",
        )
    return {"status": "success", **result}
    
@router.patch('/update-council/{council_id}', status_code = status.HTTP_200_OK)
async def updateCouncil(council: CouncilPatch, id: int, current_user=Depends(require_admin)):

    result = await fetch_one('''UPDATE council SET name = COALESCE(%s, name), resolution_count = COALESCE(%s, resolution_count) WHERE council_id = %s RETURNING *''', (council.name, council.resolution_count, id,))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Council not found",
        )
    return {"status": "success", **result}

@router.patch('/update-main-council/{council_id}', status_code=status.HTTP_200_OK)
async def updateMainCouncil(council_id: int, current_user=Depends(require_admin)):
    async with transaction() as cursor:
        await execute('''UPDATE councils SET is_main = FALSE WHERE is_main = TRUE;''', cursor=cursor)
        result = await fetch_one('''UPDATE councils SET is_main = TRUE WHERE council_id = %s;''',(council_id,),cursor=cursor)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Council not found",
        )
    return {"status": "success", **result}