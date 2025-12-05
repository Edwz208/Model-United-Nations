from fastapi import APIRouter, HTTPException, status, Depends
from schemas import Amendment, AmendmentPatch
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from helpers import require_member_or_admin, require_admin, require_specific_member_or_admin, transaction, get_cursor, fetch_all, fetch_one, execute
router = APIRouter()


async def getOwnAmendments(id: int) -> dict:
    ownAmendments = await fetch_all("""SELECT content,clause,resolution_id,submitter,status, modified_at, amendment_id from amendments WHERE (%s) = ANY(submitter)""", (id,))
    return ownAmendments
        
async def getRecentAmendments() -> dict:
    recentAmendments = await fetch_all("""SELECT content, clause, resolution_id, submitter, status, modified_at, amendment_id from amendments ORDER BY modified_at DESC LIMIT 3""")
    return recentAmendments
        
@router.get('/specific-amendment-country/{country_id}', status_code=status.HTTP_200_OK)
async def specificCountryAmendment(country_id: int):
    await require_specific_member_or_admin(country_id)    
    amendments = await getOwnAmendments(country_id)
    return amendments

@router.get('/all-amendments', status_code=status.HTTP_200_OK)
async def allAmendments(current_user=Depends(require_member_or_admin)):
    result = await fetch_all('''SELECT content, clause, resolution_id, submitter, status, modified_at, amendment_id from amendments''')
    print(result)
    return result


@router.post('/upload-amendment',status_code = status.HTTP_200_OK)
async def uploading_amendment(amendment: Amendment, current_user=Depends(require_member_or_admin)):
    amendment_count = await fetch_one('''UPDATE resolutions SET amendment_count = amendment_count +1 WHERE number = %s RETURNING amendment_count''', (amendment.resolution_id,))
    print(amendment_count.get("amendment_count"))
    amendment_id = f"{amendment.resolution_id}{amendment_count.get('amendment_count')}"
    addedAmendment = await fetch_one('''INSERT INTO amendments (content, clause, resolution_id, submitter, status, amendment_id) VALUES (%s,%s,%s,%s,%s,%s) returning *''', 
                                (amendment.content, amendment.clause, amendment.resolution_id, amendment.submitter, amendment.status, amendment_id))
    return addedAmendment
    

@router.patch('/update-amendment/{number}')
async def updateAmendment(number: int, amendment: AmendmentPatch, current_user=Depends(require_member_or_admin)):
    if current_user.get("role") == 'member': # need to check if its the same country
        result = await fetch_one('''WITH country_name as (SELECT name from countries WHERE id=%s) UPDATE amendments SET 
                                     content=COALESCE(%s, content), 
                                     clause = COALESCE(%s, clause), 
                                    submitter = COALESCE(%s, submitter), 
                                     status = COALESCE(%s, status) WHERE amendment_id = %s and (select name from country_name) =ANY(submitter) RETURNING *''',
                                     (current_user.get("id"),amendment.content, amendment.clause, amendment.submitter, amendment.status, number))
    if current_user.get("role") == 'admin':
        result = await fetch_one('''UPDATE amendments SET 
                                     content=COALESCE(%s, content), 
                                     clause = COALESCE(%s, clause), 
                                    submitter = COALESCE(%s, submitter), 
                                     status = COALESCE(%s, status) WHERE amendment_id = %s RETURNING *''',
                                     (amendment.content, amendment.clause, amendment.submitter, amendment.status, number))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Amendment was not found",
        )
    return result
        
@router.delete('/delete-amendment/{number}', status_code=status.HTTP_200_OK)
async def deleteAmendment(number: int, current_user=Depends(require_member_or_admin)):
    if current_user.get("role") == 'member':
        result = await fetch_one('''WITH country_name as (SELECT name from country WHERE id=%s), deleteAmend as (DELETE from amendments WHERE amendment_id=%s and (select name from country_name) =ANY(submitter) RETURNING * ), updateResolution as (UPDATE resolutions SET amendment_count = amendment_count -1 WHERE number = (select resolution_id from deleteAmend)) select * from deleteAmend''', (current_user.get("id"),number,))
    elif current_user.get("role") == 'admin':
        result = await fetch_one('''WITH deleteAmend as (DELETE from amendments WHERE amendment_id=%s RETURNING *), updateResolutions as (UPDATE resolutions SET amendment_count = amendment_count -1 WHERE number = (select resolution_id from deleteAmend)) select * from deleteAmend''', (number,))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resolution {number} was not found",
        )
    return result
