import os
from functools import lru_cache
from dotenv import load_dotenv
from psycopg_pool import AsyncConnectionPool
load_dotenv()
conninfo = f"host='localhost' dbname='mmun' user='postgres' password={os.getenv('DB_PASSWORD')}"


@lru_cache()
def get_async_pool():
    return AsyncConnectionPool(conninfo=conninfo)
