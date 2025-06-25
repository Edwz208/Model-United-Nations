import psycopg2 
from psycopg2.extras import RealDictCursor
import os
import time
from dotenv import load_dotenv
load_dotenv()

while True:
    try: 
        conn = psycopg2.connect(host='localhost', database='mmun', user='postgres', password=os.getenv("DB_PASSWORD"), cursor_factory=RealDictCursor)
        conn.autocommit = True
        cursor = conn.cursor()
        print("Connected to db testdb")
        break
    except Exception as error:
        print("Task Failed")
        print("Error: ", error)
        time.sleep(2)
