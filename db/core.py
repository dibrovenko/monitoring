import os
import shutil
from typing import List, Type, Literal

from sqlalchemy import Integer, and_, cast, func, insert, inspect, or_, select, text, desc
from datetime import datetime, timedelta

from banks.common_func.except_handlers import async_exception_handler
from db.database import Base, async_engine, async_session_factory
from db.models import Users, Changes, Banks, TypeChanges
from db.schemas import ChangesDTO, ChangesFULLDTO


class AsyncORM:
    # Асинхронный вариант, не показанный в видео
    @staticmethod
    async def create_tables(flag: Literal['delete', 'restart']):
        if flag == "delete":

            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)

            for bank in Banks:
                if os.path.exists(f"banks/{bank.value}/data"):
                    shutil.rmtree(f"banks/{bank.value}/data")
                    os.mkdir(f"banks/{bank.value}/data")
                else:
                    os.mkdir(f"banks/{bank.value}/data")

        elif flag == "restart":

            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            for bank in Banks:
                if not os.path.exists(f"banks/{bank.value}/data"):
                    os.mkdir(f"banks/{bank.value}/data")

        else:
            raise ValueError("Недопустимое значение аргумента")

    @staticmethod
    @async_exception_handler
    async def insert_change(class_change: Users | Changes):
        async with async_session_factory() as session:
            session.add(class_change)
            await session.commit()

    @staticmethod
    #@async_exception_handler
    async def insert_list_changes(list_class_changes: List[Users | Changes]):
        try:
            async with async_session_factory() as session:
                session.add_all(list_class_changes)
                await session.commit()
        except Exception as e:
            print(e)
            return False

    @staticmethod
    @async_exception_handler
    async def select_changes() -> type(ChangesDTO):
        async with async_session_factory() as session:
            query = (
                select(Changes)
                .limit(2)
            )
            res = await session.execute(query)
            result_orm = res.scalars().all()
            result_dto = [ChangesDTO.model_validate(row, from_attributes=True) for row in result_orm]
            print(result_dto)
            return result_dto

    @staticmethod
    @async_exception_handler
    async def select_changes_for_compare(bank: Banks.__members__, typechanges: TypeChanges.__members__,
                                         lim: int = 50) -> List[ChangesFULLDTO]:
        async with async_session_factory() as session:
            query = (
                select(Changes)
                .where(Changes.typechanges == typechanges, Changes.bank == bank)
                .order_by(desc(Changes.date))
                .limit(lim)
            )
            res = await session.execute(query)
            result_orm = res.scalars().all()
            result_dto = [ChangesFULLDTO.model_validate(row, from_attributes=True) for row in result_orm]
            #print(result_dto)
            return result_dto

    @staticmethod
    @async_exception_handler
    async def select_changes_for_daily_notification() -> List[ChangesFULLDTO]:
        async with async_session_factory() as session:
            query = (
                select(Changes).
                    filter(Changes.date > (datetime.now() - timedelta(hours=22)))
            )
            res = await session.execute(query)
            result_orm = res.scalars().all()
            result_dto = [ChangesFULLDTO.model_validate(row, from_attributes=True) for row in result_orm]
            return result_dto

    @staticmethod
    #@async_exception_handler
    async def update_date():
        async with async_session_factory() as session:
            query = (
                select(Changes)
            )
            res = await session.execute(query)
            result_orm = res.scalars().all()

            for result in result_orm:
                result.date = result.date - timedelta(days=1)
            await session.commit()