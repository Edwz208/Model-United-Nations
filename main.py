from fastapi import FastAPI, HTTPException, status, Response, APIRouter
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2 
from psycopg2.extras import RealDictCursor
from routers import memberCode
from fastapi.middleware.cors import CORSMiddleware
import time
from dotenv import load_dotenv, find_dotenv
import os
import io

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
import csv

import requests
url = os.getenv("SPREADSHEET")
response = requests.get(url)
csvString = response.text

f = io.StringIO(csvString)
reader = csv.DictReader(f)
data = list(reader)
print(data)

while True:
    try: 
        conn = psycopg2.connect(host='localhost', database='testdb', user='postgres', password=os.getenv("DB_PASSWORD"), cursor_factory=RealDictCursor)
        conn.autocommit = True
        cursor = conn.cursor()
        print("Connected to db testdb")
        break

    except Exception as error:
        print("Task Failed")
        print("Error: ", error)
        time.sleep(2)



app.include_router(memberCode.router)


