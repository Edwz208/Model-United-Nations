from fastapi import FastAPI, HTTPException, status, Response, APIRouter
from fastapi.params import Body
from pydantic import BaseModel
from routers import memberCode, createAuto, createManual
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

app = FastAPI()

origins = [
    "http://localhost:8000",  
    "http://localhost:5173",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           
    allow_credentials=True,
    allow_methods=["*"],             
    allow_headers=["*"],              
)



app.include_router(memberCode.router)
app.include_router(createAuto.router)
app.include_router(createManual.router)


