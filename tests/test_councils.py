import pytest
from services.councils import get_all_councils_service
from db.connection import AsyncConnectionPool
import asyncio
import sys
from config import settings
#pytest -s to show print
if sys.platform.startswith("win"):
    # Use a selector event loop for psycopg async
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

@pytest.mark.asyncio
async def test_get_all_council_service():
    async with AsyncConnectionPool(conninfo=settings.DATABASE_URL,
        configure=lambda conn: conn.set_autocommit(True),
        max_size=5) as pool:
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute('''DELETE FROM councils''')
                await cur.execute('''INSERT INTO councils (name) VALUES ('General Assembly'), ('Security Council')''')

    result = await get_all_councils_service()
    print(result)
    assert isinstance(result, list)
