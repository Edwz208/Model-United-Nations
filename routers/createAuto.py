from fastapi import APIRouter, HTTPException, status
import csv
import requests
import io
import os
from db import cursor

router = APIRouter()

def sanitizeKey(key):
    return key.strip().lower().replace('#', '').replace(' ', '_')

@router.get('/sheet-export')
async def sheetExport():
    url = os.getenv("SPREADSHEET")
    response = requests.get(url)
    csvString = response.text
    f = io.StringIO(csvString)
    firstLine = next(f)
    rawKeys =firstLine.strip().split(',')
    print(rawKeys)  
    sanitizedKeys = [sanitizeKey(name) for name in rawKeys]
    reader = csv.DictReader(f, fieldnames=sanitizedKeys)
    next(reader)
    data = list(reader)
    print("data")
    print(data)
    
    for dict in data:
        del dict['school']
        cursor.execute('''INSERT INTO delegates (country, delegate1, delegate2, delegate3, delegate4) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (country) DO UPDATE
SET delegate1 = EXCLUDED.delegate1,
    delegate2 = EXCLUDED.delegate2,
    delegate3 = EXCLUDED.delegate3,
    delegate4 = EXCLUDED.delegate4;''',(dict['assigned_country'], dict['delegate_1'],dict['delegate_2'],dict['delegate_3'],dict['delegate_4']))
    return data

@router.get('/get-countries')
async def getAll():
    cursor.execute('''SELECT * from delegates''')
    allCount = cursor.fetchall()
    return allCount

@router.get('/select-country/{country}')
async def selectCountry(country: str):
    cursor.execute('''SELECT * FROM delegates WHERE country=%s''', (country,))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f"Country with name {country} was not found")
    print(result)
    return result

@router.delete('/select-country/{country}')
async def deleteCountry(country: str):
    cursor.execute('''DELETE FROM delegates WHERE country = %s RETURNING *''',(country,))
    if not cursor.fetchone():
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f"Country with name {country} was not found")
    return {"message": f"{country} deleted"}

