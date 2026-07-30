# app/modules/councils/repository.py

from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.councils.models import Council

class CouncilRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> Sequence[Council]:
        result = await self.session.execute(select(Council).order_by(Council.is_main.desc(), Council.name))
        return result.scalars().all()

    async def get_by_id(self, council_id: int) -> Council | None:
        result = await self.session.execute(select(Council).where(Council.council_id == council_id))
        return result.scalar_one_or_none()

    async def create(self, council: Council) -> Council:
        self.session.add(council)
        await self.session.commit()
        await self.session.refresh(council)
        return council

    async def delete(self, council: Council) -> None:
        await self.session.delete(council)
        await self.session.commit()

    async def update(self, council: Council) -> Council:
        await self.session.commit()
        await self.session.refresh(council)
        return council

    async def set_main(self, council_id: int) -> Council | None:
        await self.session.execute(update(Council).where(Council.is_main == True).values(is_main=False))
        council = await self.get_by_id(council_id)
        if not council:
            await self.session.commit()
            return None
        council.is_main = True
        await self.session.commit()
        await self.session.refresh(council)
        return council
