import os
from functools import lru_cache
from dotenv import load_dotenv
from psycopg_pool import AsyncConnectionPool
load_dotenv()
conninfo = f"host='localhost' dbname='mmun' user='postgres' password={os.getenv('DB_PASSWORD')}"


@lru_cache() # makes it so that all with same arguments use the same instance of the object, the same pool and using its connections
def get_async_pool():
    return AsyncConnectionPool(conninfo=conninfo,configure=lambda conn: conn.set_autocommit(True)) # auto passes the conn instance created into function for autocommit, not supported in psycopg3 otherwise
