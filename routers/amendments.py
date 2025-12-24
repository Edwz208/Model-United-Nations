from fastapi import APIRouter, HTTPException, status, Depends
from schemas import Amendment, AmendmentPatch
from auth.dependencies import require_member_or_admin, require_specific_member_or_admin
from db.utils import transaction, get_cursor, fetch_all, fetch_one, execute
router = APIRouter()
 
async def getOwnAmendments(id: int) -> list[dict]:
    ownAmendments = await fetch_all("""SELECT content,clause,resolution_id,submitter,status, modified_at, amendment_id from amendments WHERE (%s) = ANY(submitter)""", (id,))
    return ownAmendments
        
async def getRecentAmendments() -> list[dict]:
    recentAmendments = await fetch_all("""SELECT content, clause, resolution_id, submitter, status, modified_at, amendment_id from amendments ORDER BY modified_at DESC LIMIT 3""")
    return recentAmendments

async def getAmendmentsPerResolution(resolution_id: int) -> list[dict]:
    amendmentsForResolution = await fetch_all("""SELECT content,clause,resolution_id,submitter,status, modified_at, amendment_id from amendments WHERE resolution_id = %s""", (resolution_id,))
    return amendmentsForResolution
        
@router.get('/specific-amendment-country/{country_id}', status_code=status.HTTP_200_OK)
async def specificCountryAmendment(country_id: int, current_user=Depends(require_specific_member_or_admin)):
    amendments = await getOwnAmendments(country_id)
    return amendments

@router.get('/all-amendments/{resolution_id}', status_code=status.HTTP_200_OK)
async def allAmendmentsForResolution(resolution_id: int, current_user=Depends(require_member_or_admin)):
    result = await getAmendmentsPerResolution(resolution_id)
    return result

@router.post('/upload-amendment',status_code = status.HTTP_200_OK)
async def uploading_amendment(amendment: Amendment, current_user=Depends(require_member_or_admin)):
    amendment_count = await fetch_one('''UPDATE resolutions SET amendment_count = amendment_count +1 WHERE number = %s RETURNING amendment_count''', (amendment.resolution_id,)) or {}
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
            detail=f"Amendment {number} was not found",
        )
    return {"status": "success", **result}
