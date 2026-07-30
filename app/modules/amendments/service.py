# app/modules/amendments/service.py

from app.modules.amendments.repository import AmendmentRepository
from app.modules.amendments.models import Amendment, AmendmentStatus
from app.modules.amendments.schemas import AmendmentOut
from app.core.exceptions import AmendmentNotFoundException, ResolutionNotFoundException, InvalidAssignmentException, ValidationException

class AmendmentService:
    def __init__(self, repository: AmendmentRepository) -> None:
        self.repository = repository

    async def get_own_amendments(self, country_id: int) -> list[AmendmentOut]:
        amendments = await self.repository.list_for_country(country_id)
        return [AmendmentOut.model_validate(amendment) for amendment in amendments]

    async def get_all_amendments_for_resolution(self, resolution_id: int) -> list[AmendmentOut]:
        amendments = await self.repository.list_for_resolution(resolution_id)
        return [AmendmentOut.model_validate(amendment) for amendment in amendments]

    async def get_all_amendments_for_council(self, council_id: int) -> list[AmendmentOut]:
        amendments = await self.repository.list_for_council(council_id)
        return [AmendmentOut.model_validate(amendment) for amendment in amendments]

    async def upload_amendment(self, content: str, clause: int, resolution_id: int, submitter: int, amendment_status: str) -> AmendmentOut:
        resolution = await self.repository.get_resolution(resolution_id)
        if not resolution:
            raise ResolutionNotFoundException(resolution_id)
        if not await self.repository.country_in_council(resolution.council_id, submitter):
            raise InvalidAssignmentException("Submitter is not a member of this council")

        amendment_number = await self.repository.next_amendment_number(resolution_id)
        amendment = Amendment(resolution_id=resolution_id, amendment_number=amendment_number, content=content, clause_number=clause, submitter=submitter, status=amendment_status)
        created = await self.repository.create(amendment)
        return AmendmentOut.model_validate(created)

    async def delete_amendment(self, amendment_id: int) -> AmendmentOut:
        amendment = await self.repository.get_by_id(amendment_id)
        if not amendment:
            raise AmendmentNotFoundException(amendment_id)
        out = AmendmentOut.model_validate(amendment)
        resolution_id = amendment.resolution_id
        await self.repository.delete(amendment)
        await self.repository.adjust_resolution_amendment_count(resolution_id, -1)
        return out

    async def approve_reject_amendment(self, amendment_id: int, amendment_status: str, rejection_message: str | None) -> AmendmentOut:
        amendment = await self.repository.get_by_id(amendment_id)
        if not amendment:
            raise AmendmentNotFoundException(amendment_id)

        if amendment_status == AmendmentStatus.REJECTED.value:
            amendment.status = AmendmentStatus.REJECTED
            amendment.content = rejection_message
        elif amendment_status == AmendmentStatus.APPROVED.value:
            amendment.status = AmendmentStatus.APPROVED
            await self.repository.adjust_resolution_amendment_count(amendment.resolution_id, 1)
        elif amendment_status == AmendmentStatus.PENDING.value:
            amendment.status = AmendmentStatus.PENDING
        else:
            raise ValidationException("Invalid amendment status")

        updated = await self.repository.update(amendment)
        return AmendmentOut.model_validate(updated)

    async def update_amendment(self, amendment_id: int, resolution_id: int | None, amendment_status: str | None, submitter: int | None, clause: int | None, content: str | None) -> AmendmentOut:
        amendment = await self.repository.get_by_id(amendment_id)
        if not amendment:
            raise AmendmentNotFoundException(amendment_id)

        target_resolution_id = resolution_id if resolution_id is not None else amendment.resolution_id
        target_submitter = submitter if submitter is not None else amendment.submitter
        resolution = await self.repository.get_resolution(target_resolution_id)
        if not resolution:
            raise ResolutionNotFoundException(target_resolution_id)
        if not await self.repository.country_in_council(resolution.council_id, target_submitter):
            raise InvalidAssignmentException("Submitter is not a member of this council")

        if resolution_id is not None:
            amendment.resolution_id = resolution_id
        if amendment_status is not None:
            amendment.status = amendment_status
        if clause is not None:
            amendment.clause_number = clause
        if submitter is not None:
            amendment.submitter = submitter
        if content is not None:
            amendment.content = content

        updated = await self.repository.update(amendment)
        return AmendmentOut.model_validate(updated)
