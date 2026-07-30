# main.py

import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import app.core.models
from app.core.middleware import setup_middleware

from app.modules.auth.router import router as login_router
from app.modules.countries.router import router as countries_data_router
from app.modules.resolution.router import router as resolutions_data_router
from app.modules.amendments.router import router as amendments_data_router
from app.modules.councils.router import router as councils_data_router
from app.modules.secretariat.router import router as secretariat_data_router
from app.modules.projection.router import router as projection_data_router

app = FastAPI()
setup_middleware(app)

logger = logging.getLogger(__name__)

app.mount("/resolutions-pdfs", StaticFiles(directory="uploads/resolutions"), name="pdfs")

@app.get("/")
async def root():
    return {"message": "Welcome"}

app.include_router(login_router)
app.include_router(countries_data_router)
app.include_router(resolutions_data_router)
app.include_router(amendments_data_router)
app.include_router(councils_data_router)
app.include_router(secretariat_data_router)
app.include_router(projection_data_router)
