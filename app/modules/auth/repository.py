# app/modules/auth/repository.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.countries.models import Country

class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_name(self, name: str) -> Country | None:
        result = await self.session.execute(select(Country).where(Country.name == name))
        return result.scalar_one_or_none()
