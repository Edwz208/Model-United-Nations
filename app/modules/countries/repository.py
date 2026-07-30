# app/modules/countries/repository.py

from typing import Sequence
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.modules.countries.models import Country, CountryRole
from app.modules.councils.models import Council

class CountryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_members(self) -> Sequence[Country]:
        result = await self.session.execute(select(Country).where(Country.role == CountryRole.MEMBER).options(selectinload(Country.councils)).order_by(Country.name))
        return result.scalars().all()

    async def get_by_id(self, country_id: int) -> Country | None:
        result = await self.session.execute(select(Country).where(Country.country_id == country_id).options(selectinload(Country.councils)))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Country | None:
        result = await self.session.execute(select(Country).where(Country.name == name))
        return result.scalar_one_or_none()

    async def get_main_council_id(self) -> int | None:
        result = await self.session.execute(select(Council.council_id).where(Council.is_main == True))
        return result.scalar_one_or_none()

    async def login_exists(self, login: str) -> bool:
        result = await self.session.execute(select(exists().where(Country.login == login)))
        return bool(result.scalar())

    async def create(self, country: Country, council_ids: list[int]) -> Country:
        self.session.add(country)
        await self.session.flush()
        if council_ids:
            councils = await self.session.execute(select(Council).where(Council.council_id.in_(council_ids)))
            country.councils = list(councils.scalars().all())
        await self.session.commit()
        await self.session.refresh(country, attribute_names=["councils"])
        return country

    async def update(self, country: Country, council_ids: list[int] | None) -> Country:
        if council_ids is not None:
            main_council_id = await self.get_main_council_id()
            keep = [council for council in country.councils if main_council_id is not None and council.council_id == main_council_id]
            councils = await self.session.execute(select(Council).where(Council.council_id.in_(council_ids)))
            merged = keep + [council for council in councils.scalars().all() if council not in keep]
            country.councils = merged
        await self.session.commit()
        await self.session.refresh(country, attribute_names=["councils"])
        return country

    async def delete_many(self, ids: list[int]) -> Sequence[Country]:
        result = await self.session.execute(select(Country).where(Country.country_id.in_(ids), Country.role != CountryRole.ADMIN))
        countries = result.scalars().all()
        for country in countries:
            await self.session.delete(country)
        await self.session.commit()
        return countries

    async def update_speaker_points(self, country: Country, delta: int) -> Country:
        country.speaker_points = country.speaker_points + delta
        await self.session.commit()
        await self.session.refresh(country)
        return country

    async def upsert_from_spreadsheet(self, name: str, delegate1: str | None, delegate2: str | None, delegate3: str | None, delegate4: str | None, login: str) -> None:
        existing = await self.get_by_name(name)
        if existing:
            existing.delegate1 = delegate1
            existing.delegate2 = delegate2
            existing.delegate3 = delegate3
            existing.delegate4 = delegate4
            if not existing.login:
                existing.login = login
            existing.role = CountryRole.MEMBER
        else:
            self.session.add(Country(name=name, delegate1=delegate1, delegate2=delegate2, delegate3=delegate3, delegate4=delegate4, login=login, speaker_points=0, role=CountryRole.MEMBER))
        await self.session.commit()
