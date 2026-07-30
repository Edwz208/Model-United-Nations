# app/modules/resolution/service.py

from pathlib import Path
from fastapi import UploadFile
from pydantic import ValidationError
from app.modules.resolution.repository import ResolutionRepository
from app.modules.resolution.models import Resolution
from app.modules.resolution.schemas import ResolutionCreateValidate, ResolutionPatch, ResolutionListOut, ResolutionDetailOut
from app.core.exceptions import ResolutionNotFoundException, CouncilNotFoundException, ValidationException, InvalidAssignmentException
from app.core.utils import file_to_directory

class ResolutionService:
    def __init__(self, repository: ResolutionRepository) -> None:
        self.repository = repository

    async def get_all_resolutions_general_info(self) -> list[ResolutionListOut]:
        resolutions = await self.repository.list_general()
        return [ResolutionListOut.model_validate(resolution) for resolution in resolutions]

    async def get_all_council_resolutions_general_info(self, council_id: int) -> list[ResolutionListOut]:
        resolutions = await self.repository.list_general_for_council(council_id)
        return [ResolutionListOut.model_validate(resolution) for resolution in resolutions]

    async def get_specific_resolution(self, resolution_id: int) -> ResolutionDetailOut:
        resolution = await self.repository.get_by_id(resolution_id)
        if not resolution:
            raise ResolutionNotFoundException(resolution_id)
        return ResolutionDetailOut.model_validate(resolution)

    async def _validate_assignment(self, council_id: int, is_main: bool, submitter: int, seconder: int, negator: int) -> None:
        if is_main:
            checks = [await self.repository.country_exists(submitter), await self.repository.country_exists(seconder), await self.repository.country_exists(negator)]
        else:
            checks = [await self.repository.country_in_council(council_id, submitter), await self.repository.country_in_council(council_id, seconder), await self.repository.country_in_council(council_id, negator)]
        if not all(checks):
            raise InvalidAssignmentException()

    async def upload_resolution(self, council_id: int, title: str, number: int, clauses: int, submitter: int, seconder: int, negator: int, file: UploadFile) -> ResolutionDetailOut:
        try:
            ResolutionCreateValidate(council_id=council_id, title=title, number=number, clauses=clauses, submitter=submitter, seconder=seconder, negator=negator)
        except ValidationError as e:
            raise ValidationException(str(e))

        council = await self.repository.get_council(council_id)
        if not council:
            raise CouncilNotFoundException(council_id)

        await self._validate_assignment(council_id, council.is_main, submitter, seconder, negator)

        url = file_to_directory(file)
        resolution = Resolution(council_id=council_id, title=title, url=url, number=number, clauses=clauses, submitter=submitter, seconder=seconder, negator=negator)
        created = await self.repository.create(resolution)
        await self.repository.increment_council_count(council_id, 1)
        return ResolutionDetailOut.model_validate(created)

    async def update_resolution(self, title: str | None, council_id: int | None, res_status: str | None, clauses: int | None, submitter: int | None, seconder: int | None, negator: int | None, number: int | None, file: UploadFile | None, resolution_id: int) -> ResolutionDetailOut:
        try:
            patch = ResolutionPatch(title=title, council_id=council_id, clauses=clauses, submitter=submitter, seconder=seconder, negator=negator, number=number, res_status=res_status)
        except ValidationError as e:
            raise ValidationException(str(e))

        resolution = await self.repository.get_by_id(resolution_id)
        if not resolution:
            raise ResolutionNotFoundException(resolution_id)

        target_council_id = patch.council_id if patch.council_id is not None else resolution.council_id
        council = await self.repository.get_council(target_council_id)
        if not council:
            raise CouncilNotFoundException(target_council_id)

        submitter_check = patch.submitter if patch.submitter is not None else resolution.submitter
        seconder_check = patch.seconder if patch.seconder is not None else resolution.seconder
        negator_check = patch.negator if patch.negator is not None else resolution.negator
        if submitter_check is not None and seconder_check is not None and negator_check is not None:
            await self._validate_assignment(target_council_id, council.is_main, submitter_check, seconder_check, negator_check)

        if patch.title is not None:
            resolution.title = patch.title
        if patch.council_id is not None:
            resolution.council_id = patch.council_id
        if patch.res_status is not None:
            resolution.status = patch.res_status
        if patch.clauses is not None:
            resolution.clauses = patch.clauses
        if patch.submitter is not None:
            resolution.submitter = patch.submitter
        if patch.seconder is not None:
            resolution.seconder = patch.seconder
        if patch.negator is not None:
            resolution.negator = patch.negator
        if patch.number is not None:
            resolution.number = patch.number
        if file and file.filename:
            resolution.url = file_to_directory(file)

        updated = await self.repository.update(resolution)
        return ResolutionDetailOut.model_validate(updated)

    async def delete_resolutions(self, resolution_ids: list[int]) -> list[ResolutionDetailOut]:
        deleted = await self.repository.delete_many(resolution_ids)
        if not deleted:
            raise ResolutionNotFoundException()

        council_deltas: dict[int, int] = {}
        for resolution in deleted:
            if resolution.url:
                file = Path(f'./uploads/resolutions/{resolution.url}')
                if file.exists():
                    file.unlink()
            council_deltas[resolution.council_id] = council_deltas.get(resolution.council_id, 0) + 1

        for council_id, count in council_deltas.items():
            await self.repository.increment_council_count(council_id, -count)

        return [ResolutionDetailOut.model_validate(resolution) for resolution in deleted]
