from typing import List
from sqlalchemy import Integer, and_, cast, func, insert, inspect, or_, select, text

from banks.common_func.except_handlers import async_exception_handler
from db.database import Base, async_engine, async_session_factory
from db.models import Users, Changes, Banks, TypeChanges
from db.schemas import ChangesDTO, ChangesFULLDTO


class AsyncORM:
    # Асинхронный вариант, не показанный в видео
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            #await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    @async_exception_handler
    async def insert_change(class_change: Users | Changes):
        async with async_session_factory() as session:
            session.add(class_change)
            await session.commit()

    @staticmethod
    @async_exception_handler
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
    async def select_changes() -> ChangesDTO:
        async with async_session_factory() as session:
            query = (
                select(Changes)
                .limit(2)
            )
            res = await session.execute(query)
            result_orm = res.scalars().all()
            print(f"{result_orm=}")
            result_dto = [ChangesDTO.model_validate(row, from_attributes=True) for row in result_orm]
            print(f"{result_dto=}")
            return result_dto

    @staticmethod
    @async_exception_handler
    async def select_changes_for_compare(bank: Banks.__members__, typechanges: TypeChanges.__members__,
                                         lim: int = 50) -> ChangesFULLDTO:
        async with async_session_factory() as session:
            query = (
                select(Changes)
                .where(Changes.typechanges == typechanges and Changes.bank == bank)
                .order_by(Changes.date)
                .limit(lim)
            )
            res = await session.execute(query)
            result_orm = res.scalars().all()
            result_dto = [ChangesFULLDTO.model_validate(row, from_attributes=True) for row in result_orm]
            print(f"{result_dto=}")
            return result_dto
