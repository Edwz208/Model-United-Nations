# app/modules/resolution/repository.py

from typing import Sequence
from sqlalchemy import select, exists, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.resolution.models import Resolution
from app.modules.councils.models import Council
from app.modules.countries.models import Country
from app.core.associations import country_council

class ResolutionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_general(self) -> Sequence[Resolution]:
        result = await self.session.execute(select(Resolution).order_by(Resolution.title))
        return result.scalars().all()

    async def list_general_for_council(self, council_id: int) -> Sequence[Resolution]:
        result = await self.session.execute(select(Resolution).where(Resolution.council_id == council_id))
        return result.scalars().all()

    async def get_by_id(self, resolution_id: int) -> Resolution | None:
        result = await self.session.execute(select(Resolution).where(Resolution.resolution_id == resolution_id))
        return result.scalar_one_or_none()

    async def get_council(self, council_id: int) -> Council | None:
        result = await self.session.execute(select(Council).where(Council.council_id == council_id))
        return result.scalar_one_or_none()

    async def country_exists(self, country_id: int) -> bool:
        result = await self.session.execute(select(exists().where(Country.country_id == country_id)))
        return bool(result.scalar())

    async def country_in_council(self, council_id: int, country_id: int) -> bool:
        result = await self.session.execute(select(exists().where(and_(country_council.c.council_id == council_id, country_council.c.country_id == country_id))))
        return bool(result.scalar())

    async def create(self, resolution: Resolution) -> Resolution:
        self.session.add(resolution)
        await self.session.commit()
        await self.session.refresh(resolution)
        return resolution

    async def update(self, resolution: Resolution) -> Resolution:
        await self.session.commit()
        await self.session.refresh(resolution)
        return resolution

    async def delete_many(self, ids: list[int]) -> Sequence[Resolution]:
        result = await self.session.execute(select(Resolution).where(Resolution.resolution_id.in_(ids)))
        resolutions = result.scalars().all()
        for resolution in resolutions:
            await self.session.delete(resolution)
        await self.session.commit()
        return resolutions

    async def increment_council_count(self, council_id: int, delta: int) -> None:
        council = await self.get_council(council_id)
        if council:
            council.resolution_count = council.resolution_count + delta
            await self.session.commit()
