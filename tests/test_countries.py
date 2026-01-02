from services.countries import get_countries_general_service
import pytest

@pytest.mark.asyncio
async def test_get_countries_general_service():
    result = await get_countries_general_service()
    print(result)
    assert result == []