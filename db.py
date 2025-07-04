import os
from dotenv import load_dotenv

load_dotenv()
from functools import lru_cache
from psycopg_pool import AsyncConnectionPool

conninfo = f"host='localhost' dbname='mmun' user='postgres' password={os.getenv("DB_PASSWORD")}"


@lru_cache()
def get_async_pool():
    return AsyncConnectionPool(conninfo=conninfo)
