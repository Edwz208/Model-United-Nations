from functools import lru_cache
from psycopg_pool import AsyncConnectionPool # Creates a pool of connections that can work asynchronously
from config import settings

import asyncio
import sys
if sys.platform.startswith("win"):
    # Use a selector event loop for psycopg async
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
@lru_cache() # decorator that all function calls with the same arguments use the same instance of the object, thus using the same pool and connections
def get_async_pool() -> AsyncConnectionPool:
    return AsyncConnectionPool(conninfo=settings.DATABASE_URL,
        configure=lambda conn: conn.set_autocommit(True),
        max_size=5) # callback function that is triggered everytime a connection is formed,
# auto passes the conn instance created into a function lambda that took the took the conn as an argument and enabled autocommit because psycopg3 does not have autocommit passing directly to a pool or connection
