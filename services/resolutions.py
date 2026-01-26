from db.utils import fetch_all, fetch_one, transaction, execute
from typing import Any
from fastapi import HTTPException, status, UploadFile
from pathlib import Path
from utils.utils import file_to_directory
from schemas import Resolution, ResolutionPatch
from pydantic import ValidationError

async def get_all_resolutions_general_info_service() -> list[dict[str, Any]]:
    result = await fetch_all('''SELECT number, title, clauses, council_id, status, amendment_count, resolution_id FROM resolutions ORDER BY LOWER(title) ASC''')
    return result

async def get_all_council_resolutions_general_info_service(council_id: int) -> list[dict[str, Any]]:
    result = await fetch_all('''SELECT number, title, clauses, status, amendment_count, resolution_id, council_id FROM resolutions WHERE council_id = %s''', (council_id,))
    return result

async def get_specific_resolution_service(resolution_id: int) -> dict[str, Any]:
    resolution = await fetch_one('''SELECT number, title, clauses, status, council_id, amendment_count, resolution_id, submitter, seconder, negator FROM resolutions WHERE resolution_id = %s''', (resolution_id,))
    if not resolution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resolution not found")
    return resolution

async def delete_resolution_service(resolution_ids: list[int]) -> list[dict[str, Any]]:
    async with transaction() as cursor:
        result = await fetch_all('''DELETE FROM resolutions WHERE resolution_id=%s RETURNING *''' , (resolution_ids,), cursor=cursor)
        councils_deleted_from_counter = {}
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resolutions {resolution_ids} were not found",
            )
        for row in result:
            if row.get("url"):
                file = Path(f'./uploads/resolutions/{row.get("url")}')
                if file.exists():
                    file.unlink()
            if row["council_id"] not in councils_deleted_from_counter:
                councils_deleted_from_counter[row["council_id"]] = 1
            else: 
                councils_deleted_from_counter[row["council_id"]] +=1    

        for council_id in councils_deleted_from_counter:
                await execute('''UPDATE councils SET resolution_count = resolution_count-1 WHERE council_id = %s RETURNING resolution_count''', (councils_deleted_from_counter[council_id],), cursor=cursor)
    return result
    
async def upload_resolution_service(
    council_id: int,
    title: str,
    number: int,
    clauses: int,
    submitter: int,
    seconder: int,
    negator: int,
    file: UploadFile
):
    url = file_to_directory(file)

    try:
        Resolution(
            council_id=council_id,
            title=title,
            number=number,
            clauses=clauses,
            submitter=submitter,
            seconder=seconder,
            negator=negator
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e)

    async with transaction() as cursor:
        council = await fetch_one(
            "SELECT is_main FROM councils WHERE council_id = %s",
            (council_id,),
            cursor=cursor
        )
        if not council:
            raise HTTPException(status_code=404, detail="Council not found")

        is_main = bool(council["is_main"])

        if is_main:
            sql = '''
            INSERT INTO resolutions (council_id, title, url, number, clauses, submitter, seconder, negator)
            SELECT %s, %s, %s, %s, %s, %s, %s, %s
            WHERE EXISTS (SELECT 1 FROM countries WHERE country_id = %s)
              AND EXISTS (SELECT 1 FROM countries WHERE country_id = %s)
              AND EXISTS (SELECT 1 FROM countries WHERE country_id = %s)
            RETURNING *;
            '''
            params = (
                council_id, title, url, number, clauses, submitter, seconder, negator,
                submitter, seconder, negator
            )
        else:
            sql = '''
            INSERT INTO resolutions (council_id, title, url, number, clauses, submitter, seconder, negator)
            SELECT %s, %s, %s, %s, %s, %s, %s, %s
            WHERE EXISTS (SELECT 1 FROM country_council WHERE council_id = %s AND country_id = %s)
              AND EXISTS (SELECT 1 FROM country_council WHERE council_id = %s AND country_id = %s)
              AND EXISTS (SELECT 1 FROM country_council WHERE council_id = %s AND country_id = %s)
            RETURNING *;
            '''
            params = (
                council_id, title, url, number, clauses, submitter, seconder, negator,
                council_id, submitter,
                council_id, seconder,
                council_id, negator
            )

        resolution = await fetch_one(sql, params, cursor=cursor)

        if not resolution:
            raise HTTPException(
                status_code=404,
                detail="Submitter / seconder / negator not valid for this council"
            )

        await execute(
            "UPDATE councils SET resolution_count = resolution_count + 1 WHERE council_id = %s",
            (council_id,),
            cursor=cursor
        )

        return resolution



async def update_resolution_service(title: str | None, council_id: int | None, res_status: str | None, clauses: int | None, submitter: int | None, seconder: int | None, negator: int | None, number: int | None, file: UploadFile | None, resolution_id: int) -> dict[str, Any]:
    try: 
        resolution = ResolutionPatch(title=title, council_id=council_id, clauses=clauses, submitter=submitter, seconder=seconder, negator=negator, number=number, res_status=res_status)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e)
    if file and file.filename: 
        url = file_to_directory(file)
    else:
        url = None
        
    result = await fetch_one('''UPDATE resolutions r SET 
                        title = COALESCE(%s, title),
                        council_id = COALESCE(%s, council_id), 
                        status=COALESCE(%s, status), 
                        clauses= COALESCE(%s, clauses), 
                        submitter = COALESCE(%s, submitter), 
                        seconder = COALESCE(%s, seconder), 
                        negator = COA   LESCE(%s, negator), 
                        url = COALESCE(%s, url),
                        number = COALESCE(%s, number)
                        FROM country_council cc1 JOIN country_council cc2 ON cc1.council_id = cc2.council_id JOIN country_council cc3 ON cc3.council_id = cc1,council_id WHERE r.council_id = cc1.council_id AND cc1.country_id = COALESCE(%s, r.submitter) AND cc2.country_id = COALESCE(%s, r.seconder) AND cc3.country_id = COALESCE(%s, r.negator) RETURNING *''', (resolution.title,resolution.council_id, resolution.res_status, resolution.clauses, resolution.submitter, resolution.seconder, resolution.negator, url, resolution.number, resolution_id))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resolution was not successfully created"
            )
    return result