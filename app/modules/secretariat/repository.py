# app/modules/secretariat/repository.py

from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.secretariat.models import Secretariat

class SecretariatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> Sequence[Secretariat]:
        result = await self.session.execute(select(Secretariat).order_by(Secretariat.secretariat_id))
        return result.scalars().all()

    async def get_by_id(self, secretariat_id: int) -> Secretariat | None:
        result = await self.session.execute(select(Secretariat).where(Secretariat.secretariat_id == secretariat_id))
        return result.scalar_one_or_none()

    async def create(self, member: Secretariat) -> Secretariat:
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def delete(self, member: Secretariat) -> None:
        await self.session.delete(member)
        await self.session.commit()

    async def update(self, member: Secretariat) -> Secretariat:
        await self.session.commit()
        await self.session.refresh(member)
        return member
