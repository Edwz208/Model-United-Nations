# app/modules/countries/service.py

from random import randrange
import requests
import csv
import io
from app.modules.countries.repository import CountryRepository
from app.modules.countries.models import Country
from app.modules.countries.schemas import CountryIn, CountryPatch, CountryListOut, CountryProfileOut
from app.core.exceptions import CountryNotFoundException, InvalidSpreadsheetException
from app.core.utils import sanitize_key

class CountryService:
    def __init__(self, repository: CountryRepository) -> None:
        self.repository = repository

    def _to_list_out(self, country: Country, main_council_id: int | None) -> CountryListOut:
        council_ids = [council.council_id for council in country.councils]
        if main_council_id is not None and main_council_id not in council_ids:
            council_ids = sorted(council_ids + [main_council_id])
        return CountryListOut(country_id=country.country_id, name=country.name, amendments_submitted=country.amendments_submitted, speaker_points=country.speaker_points, role=country.role, councils=council_ids, main_council=main_council_id)

    def _to_profile_out(self, country: Country, main_council_id: int | None, include_login: bool) -> CountryProfileOut:
        council_ids = [council.council_id for council in country.councils]
        return CountryProfileOut(country_id=country.country_id, name=country.name, delegate1=country.delegate1, delegate2=country.delegate2, delegate3=country.delegate3, delegate4=country.delegate4, login=country.login if include_login else None, amendments_submitted=country.amendments_submitted, speaker_points=country.speaker_points, role=country.role, councils=council_ids, main_council=main_council_id if main_council_id in council_ids else None)

    async def get_countries_general(self) -> list[CountryListOut]:
        main_council_id = await self.repository.get_main_council_id()
        countries = await self.repository.list_members()
        return [self._to_list_out(country, main_council_id) for country in countries]

    async def get_single_country(self, target_id: int, sender_id: int, role: str) -> CountryProfileOut:
        country = await self.repository.get_by_id(target_id)
        if not country:
            raise CountryNotFoundException(target_id)
        main_council_id = await self.repository.get_main_council_id()
        include_login = sender_id == target_id or role == "admin"
        return self._to_profile_out(country, main_council_id, include_login)

    async def add_country(self, country: CountryIn) -> CountryProfileOut:
        entity = Country(name=country.assigned_country, delegate1=country.delegate1, delegate2=country.delegate2, delegate3=country.delegate3, delegate4=country.delegate4, role=country.role or "member", login=country.login, amendments_submitted=country.amendments_submitted or 0, speaker_points=country.speaker_points or 0)
        created = await self.repository.create(entity, country.councils)
        main_council_id = await self.repository.get_main_council_id()
        return self._to_profile_out(created, main_council_id, True)

    async def update_country(self, country: CountryPatch, country_id: int) -> CountryProfileOut:
        existing = await self.repository.get_by_id(country_id)
        if not existing:
            raise CountryNotFoundException(country_id)
        if country.assigned_country is not None:
            existing.name = country.assigned_country
        if country.delegate1 is not None:
            existing.delegate1 = country.delegate1
        if country.delegate2 is not None:
            existing.delegate2 = country.delegate2
        if country.delegate3 is not None:
            existing.delegate3 = country.delegate3
        if country.delegate4 is not None:
            existing.delegate4 = country.delegate4
        if country.login is not None:
            existing.login = country.login
        if country.amendments_submitted is not None:
            existing.amendments_submitted = country.amendments_submitted
        if country.speaker_points is not None:
            existing.speaker_points = country.speaker_points
        updated = await self.repository.update(existing, country.councils)
        main_council_id = await self.repository.get_main_council_id()
        return self._to_profile_out(updated, main_council_id, True)

    async def delete_countries(self, ids: list[int]) -> list[CountryProfileOut]:
        deleted = await self.repository.delete_many(ids)
        if not deleted:
            raise CountryNotFoundException()
        return [self._to_profile_out(country, None, True) for country in deleted]

    async def update_speaker_points(self, country: int, speaker_points: int) -> CountryProfileOut:
        existing = await self.repository.get_by_id(country)
        if not existing:
            raise CountryNotFoundException(country)
        updated = await self.repository.update_speaker_points(existing, speaker_points)
        main_council_id = await self.repository.get_main_council_id()
        return self._to_profile_out(updated, main_council_id, True)

    async def unique_login(self) -> str:
        while True:
            random_num = str(randrange(100000, 1000000))
            if not await self.repository.login_exists(random_num):
                return random_num

    async def import_from_sheet(self, url: str) -> None:
        try:
            response = requests.get(url)
        except Exception:
            raise InvalidSpreadsheetException("Invalid url")

        csv_string = response.text
        f = io.StringIO(csv_string)
        first_line = next(f)
        raw_keys = first_line.strip().split(",")
        sanitized_keys = [sanitize_key(name) for name in raw_keys]
        reader = csv.DictReader(f, fieldnames=sanitized_keys)
        data = list(reader)
        for row in data:
            name = row.get("assigned_country", "").strip()
            if not name and not any((v or "").strip() for v in row.values()):
                continue
            if name.lower() == "schools":
                break
            login = await self.unique_login()
            await self.repository.upsert_from_spreadsheet(name, row.get("delegate_1"), row.get("delegate_2"), row.get("delegate_3"), row.get("delegate_4"), login)
