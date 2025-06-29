from fastapi import FastAPI
from routers import countryData, login
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv
from db import get_async_pool
from contextlib import asynccontextmanager
import asyncio
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

app = FastAPI()
async_pool = get_async_pool()

origins = [
    "http://localhost:8000",
    "http://localhost:5173",
]

async def check_async_connections():
    while True:
        await asyncio.sleep(600)
        print("check async connections health")
        await async_pool.check()
        

@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await get_async_pool().open()
    task = asyncio.create_task(check_async_connections())
    yield
    task.cancel()
    await get_async_pool().close()

app = FastAPI(lifespan=lifespan_handler)
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


app.include_router(login.router)
app.include_router(countryData.router)
