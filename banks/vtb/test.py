import os
from typing import List
from sqlalchemy import Integer, and_, cast, func, insert, inspect, or_, select, text, desc
from datetime import datetime, timedelta

from banks.common_func.except_handlers import async_exception_handler
from db.database import Base, async_engine, async_session_factory
from db.models import Users, Changes, Banks, TypeChanges
from db.schemas import ChangesDTO, ChangesFULLDTO


async def update_title(typechanges: TypeChanges.__members__,
                       title_old: str | None = None, title_new: str | None = None):
    async with async_session_factory() as session:
        if title_new is None:
            # Находим последнюю запись по дате
            latest_record: ChangesFULLDTO = (
                await session.execute(
                    select(Changes)
                    .filter(Changes.bank == Banks.vtb, Changes.typechanges == typechanges)
                    .order_by(Changes.date)
                    .limit(1)
                )
            ).scalar()
            # Модифицируем значения в найденной записи
            if latest_record:
                latest_record.title = "Измененная запись"
                await session.commit()
        else:
            latest_record: ChangesFULLDTO = (
                await session.execute(
                    select(Changes)
                        .filter(Changes.bank == Banks.vtb, Changes.typechanges == typechanges, Changes.title == title_old)
                )
            ).scalar()
            # Модифицируем значения в найденной записи
            if latest_record:
                latest_record.title = title_new
                await session.commit()


async def update_metadata(typechanges: TypeChanges.__members__, new_metadata: str, de_sc: bool | None = None):
    async with async_session_factory() as session:
        if de_sc is None:
            # Находим последнюю запись по дате
            latest_record: ChangesFULLDTO = (
                await session.execute(
                    select(Changes)
                    .filter(Changes.bank == Banks.vtb, Changes.typechanges == typechanges)
                    .order_by(Changes.date)
                    .limit(1)
                )
            ).scalar()
        else:
            # Находим последнюю запись по дате
            latest_record: ChangesFULLDTO = (
                await session.execute(
                    select(Changes)
                        .filter(Changes.bank == Banks.vtb, Changes.typechanges == typechanges)
                        .order_by(desc(Changes.date))
                        .limit(1)
                )
            ).scalar()

        # Модифицируем значения в найденной записи
        if latest_record:
            latest_record.meta_data = new_metadata
            await session.commit()


async def update_new_link(typechanges: TypeChanges.__members__, new_link: str):
    async with async_session_factory() as session:
        # Находим последнюю запись по дате
        latest_record: ChangesFULLDTO = (
            await session.execute(
                select(Changes)
                .filter(Changes.bank == Banks.vtb, Changes.typechanges == typechanges)
                .order_by(Changes.date)
                .limit(1)
            )
        ).scalar()

        # Модифицируем значения в найденной записи
        if latest_record:
            latest_record.link_new_file = new_link
            await session.commit()


async def test_all():
    await update_title(typechanges=TypeChanges.news)



    await update_metadata(typechanges=TypeChanges.pdf_file,
                          new_metadata="""
                          pikepdf.Dictionary({
                              "/CreationDate": test,
                              "/ModDate": "D:20240131001912+03'00'",
                              "/Producer": "iText 2.1.7 by 1T3XT"
                          })"""
                          )
    await update_metadata(typechanges=TypeChanges.pdf_file, new_metadata="Действует с 03.09.2023 146423", de_sc=True)

    await update_new_link(typechanges=TypeChanges.landing_page,
                          new_link=f'{os.getcwd()}/banks/vtb/test_landing_page.xlsx')