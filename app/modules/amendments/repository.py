# app/modules/amendments/repository.py

from typing import Sequence
from sqlalchemy import select, exists, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.amendments.models import Amendment
from app.modules.resolution.models import Resolution
from app.core.associations import country_council

class AmendmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_country(self, country_id: int) -> Sequence[Amendment]:
        result = await self.session.execute(select(Amendment).where(Amendment.submitter == country_id).order_by(Amendment.modified_at))
        return result.scalars().all()

    async def list_for_resolution(self, resolution_id: int) -> Sequence[Amendment]:
        result = await self.session.execute(select(Amendment).where(Amendment.resolution_id == resolution_id).order_by(Amendment.modified_at))
        return result.scalars().all()

    async def list_for_council(self, council_id: int) -> Sequence[Amendment]:
        result = await self.session.execute(select(Amendment).join(Resolution, Resolution.resolution_id == Amendment.resolution_id).where(Resolution.council_id == council_id).order_by(Amendment.modified_at))
        return result.scalars().all()

    async def get_by_id(self, amendment_id: int) -> Amendment | None:
        result = await self.session.execute(select(Amendment).where(Amendment.amendment_id == amendment_id))
        return result.scalar_one_or_none()

    async def get_resolution(self, resolution_id: int) -> Resolution | None:
        result = await self.session.execute(select(Resolution).where(Resolution.resolution_id == resolution_id))
        return result.scalar_one_or_none()

    async def country_in_council(self, council_id: int, country_id: int) -> bool:
        result = await self.session.execute(select(exists().where(and_(country_council.c.council_id == council_id, country_council.c.country_id == country_id))))
        return bool(result.scalar())

    async def next_amendment_number(self, resolution_id: int) -> int:
        result = await self.session.execute(select(func.max(Amendment.amendment_number)).where(Amendment.resolution_id == resolution_id))
        current_max = result.scalar()
        return (current_max or 0) + 1

    async def create(self, amendment: Amendment) -> Amendment:
        self.session.add(amendment)
        await self.session.commit()
        await self.session.refresh(amendment)
        return amendment

    async def update(self, amendment: Amendment) -> Amendment:
        await self.session.commit()
        await self.session.refresh(amendment)
        return amendment

    async def delete(self, amendment: Amendment) -> None:
        await self.session.delete(amendment)
        await self.session.commit()

    async def adjust_resolution_amendment_count(self, resolution_id: int, delta: int) -> None:
        resolution = await self.get_resolution(resolution_id)
        if resolution:
            resolution.amendment_count = resolution.amendment_count + delta
            await self.session.commit()
