# app/modules/councils/service.py

from app.modules.councils.repository import CouncilRepository
from app.modules.councils.models import Council
from app.modules.councils.schemas import CouncilOut
from app.core.exceptions import CouncilNotFoundException

class CouncilService:
    def __init__(self, repository: CouncilRepository) -> None:
        self.repository = repository

    async def get_all_councils(self) -> list[CouncilOut]:
        councils = await self.repository.list_all()
        return [CouncilOut.model_validate(council) for council in councils]

    async def post_council(self, name: str, resolution_count: int) -> CouncilOut:
        council = await self.repository.create(Council(name=name, resolution_count=resolution_count))
        return CouncilOut.model_validate(council)

    async def delete_council(self, council_id: int) -> CouncilOut:
        council = await self.repository.get_by_id(council_id)
        if not council:
            raise CouncilNotFoundException(council_id)
        out = CouncilOut.model_validate(council)
        await self.repository.delete(council)
        return out

    async def update_council(self, name: str | None, resolution_count: int | None, council_id: int) -> CouncilOut:
        council = await self.repository.get_by_id(council_id)
        if not council:
            raise CouncilNotFoundException(council_id)
        if name is not None:
            council.name = name
        if resolution_count is not None:
            council.resolution_count = resolution_count
        updated = await self.repository.update(council)
        return CouncilOut.model_validate(updated)

    async def update_main_council(self, council_id: int) -> CouncilOut:
        council = await self.repository.set_main(council_id)
        if not council:
            raise CouncilNotFoundException(council_id)
        return CouncilOut.model_validate(council)
