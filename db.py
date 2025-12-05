import os
from functools import lru_cache
from psycopg_pool import AsyncConnectionPool # Creates a pool of connections that can work asynchronously
from dotenv import load_dotenv
load_dotenv() # must keep
conninfo = os.getenv("DATABASE_URL")

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

conninfo = (
    "postgresql://postgres.xxrjiyweylckankmegwc:2RzmfylGePVniB4@aws-1-ca-central-1.pooler.supabase.com:5432/postgres"
)
@lru_cache() # decorator that all function calls with the same arguments use the same instance of the object, thus using the same pool and connections
def get_async_pool() -> AsyncConnectionPool:
    return AsyncConnectionPool(conninfo=conninfo,
        configure=lambda conn: conn.set_autocommit(True),
        max_size=5) # callback function that is triggered everytime a connection is formed,
# auto passes the conn instance created into a function lambda that took the took the conn as an argument and enabled autocommit because psycopg3 does not have autocommit passing directly to a pool or connection
