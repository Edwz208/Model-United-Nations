from fastapi import APIRouter, status, HTTPException
from schemas import Country
from db import cursor

router = APIRouter()

@router.post('/single-country')
async def oneCountry(country: Country):
            print(country.assigned_country)
            cursor.execute('''INSERT INTO delegates (country, delegate1, delegate2, delegate3, delegate4) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (country) 
                           DO UPDATE SET delegate1 = EXCLUDED.delegate1, delegate2 = EXCLUDED.delegate2, delegate3 = EXCLUDED.delegate3, delegate4 = EXCLUDED.delegate4 RETURNING *;''',
                           (country.assigned_country, country.delegate1,country.delegate2,country.delegate3,country.delegate4))
            return cursor.fetchone()
            