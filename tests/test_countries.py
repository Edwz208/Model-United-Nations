from routers import countryData
import sys
import asyncio

if sys.platform.startswith("win"):
    from asyncio import WindowsSelectorEventLoopPolicy
    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())


async def main():
    result = await countryData.getCountriesGeneral()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
 #python -m tests.test_countries to run backend as import root