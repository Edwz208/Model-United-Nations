from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from db import get_async_pool
from psycopg.rows import dict_row
from authentication import get_current_user
from typing import Annotated
from schemas import Resolution
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pool = get_async_pool()