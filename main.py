# from dotenv import load_dotenv, find_dotenv
# # make sure this goes before any imports
# dotenv_path = find_dotenv()
# load_dotenv(dotenv_path)

from routers.login import router as login_router
from backend.routers.countries import router as countries_data_router
from backend.routers.resolutions import router as resolutions_data_router
from backend.routers.amendments import router as amendments_data_router
from backend.routers.councils import router as councils_data_router
from backend.routers.secretariat import router as secretariat_data_router
from backend.routers.projection import router as projection_data_router

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

from backend.db.connection import get_async_pool
from contextlib import asynccontextmanager
import asyncio  

async def check_async_connections() -> None:
    while True:
        await asyncio.sleep(600)
        print("check async connections health")
        await get_async_pool().check()
        
@asynccontextmanager # Async context manager allows for an async function to set up and remove resources upon startup and shutdown
async def lifespan_handler(app: FastAPI):
    await get_async_pool().open() # not needed for tests, itll create a conn when needed
    
    task = asyncio.create_task(check_async_connections()) # background task that constantly occurs, at the same time as other event based tasks
    yield # pause here until the app is shutting down
    task.cancel()
    await get_async_pool().close()

app = FastAPI(lifespan=lifespan_handler)
origins = [
    "http://localhost:8000",
    "http://localhost:5173",
]   
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # allows for cookiese
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization"],
) 
    
app.mount("/resolutions-pdfs", StaticFiles(directory="uploads/resolutions"), name="pdfs") # served from localhost80000 because server

app.include_router(login_router) 
app.include_router(countries_data_router)
app.include_router(resolutions_data_router)
app.include_router(amendments_data_router)
app.include_router(councils_data_router)
app.include_router(secretariat_data_router)
app.include_router(projection_data_router)
