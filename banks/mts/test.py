from sqlalchemy import Integer, and_, cast, func, insert, inspect, or_, select, text, desc
from datetime import datetime, timedelta

from banks.common_func.except_handlers import async_exception_handler
from db.database import Base, async_engine, async_session_factory
from db.models import Users, Changes, Banks, TypeChanges
from db.schemas import ChangesDTO, ChangesFULLDTO


async def update_metadata(typechanges: TypeChanges.__members__, new_metadata: str):
    async with async_session_factory() as session:
        # Находим последнюю запись по дате
        latest_record: ChangesFULLDTO = (
            await session.execute(
                select(Changes)
                    .filter(Changes.bank == Banks.mts, Changes.typechanges == typechanges)
                    .order_by(Changes.date)
                    .limit(1)
            )
        ).scalar()

        # Модифицируем значения в найденной записи
        if latest_record:
            latest_record.meta_data = new_metadata
            await session.commit()


async def test_all():
    await update_metadata(typechanges=TypeChanges.pdf_file, new_metadata="test1")