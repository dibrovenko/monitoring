import asyncio
from banks.main_job import execute_once_daily
from db.core import AsyncORM
from db.models import Changes, Banks, TypeChanges


async def startup():
    await AsyncORM.create_tables()
    await execute_once_daily()

if __name__ == '__main__':
    asyncio.run(startup())
    #loop.run_until_complete(execute_once_daily())
