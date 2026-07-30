# tests/test_councils.py

import pytest
from app.modules.councils.service import CouncilService
from app.modules.councils.models import Council

class FakeCouncilRepository:
    def __init__(self, councils):
        self.councils = councils

    async def list_all(self):
        return self.councils

@pytest.mark.asyncio
async def test_get_all_councils_service():
    councils = [Council(council_id=1, name="General Assembly", resolution_count=0, is_main=False), Council(council_id=2, name="Security Council", resolution_count=0, is_main=True)]
    service = CouncilService(FakeCouncilRepository(councils))

    result = await service.get_all_councils()

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].name == "General Assembly"
