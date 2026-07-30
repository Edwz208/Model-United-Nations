# tests/test_countries.py

import pytest
from app.modules.countries.service import CountryService

class FakeCountryRepository:
    def __init__(self):
        self.countries = []

    async def list_members(self):
        return self.countries

    async def get_main_council_id(self):
        return None

@pytest.mark.asyncio
async def test_get_countries_general_service_empty():
    service = CountryService(FakeCountryRepository())
    result = await service.get_countries_general()
    assert result == []
