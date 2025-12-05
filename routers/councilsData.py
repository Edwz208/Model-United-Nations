from fastapi import APIRouter, HTTPException, status, Depends
from schemas import Council, CouncilPatch
from helpers import require_member_or_admin, require_admin, fetch_all, fetch_one, execute
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()

async def getCouncilsList() -> dict:
    allCouncils = await fetch_all('''SELECT council_id, name, resolution_count from councils''')
    return allCouncils

@router.get('/get-councils-list', status_code=status.HTTP_200_OK)
async def genResolutionsRoute(current_user=Depends(require_member_or_admin)):
    resolutions = await getCouncilsList()
    return resolutions