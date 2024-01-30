import pandas as pd
import os

from aiogram import types, Dispatcher
from sqlalchemy import select

from bot_tg.create_bot import dp, bot
from db.database import Base, async_engine, async_session_factory
from db.models import Users, Changes, Banks, TypeChanges


# Обработчик команды /send_file
#@dp.message_handler(commands=['send_file'])
async def send_file(message: types.Message):
    await message.answer("Отправляем базу данных. Для работы рекомендуем использовать DB Browser for SQLite."
                         " Если файл не удалось отправить, пожалуйста, сообщите администратору @paveldibr.")
    file_path = "example.db"
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            await message.answer_document(file)


# Обработчик команды /export_excel
#@dp.message_handler(commands=['export_excel'])
async def export_excel(message: types.Message):
    await message.answer("Если не удалось отправить файл Excel, пожалуйста, сообщите администратору @paveldibr.")
    async with async_session_factory() as session:
        query = (
            select(Changes)
        )
        res = await session.execute(query)
        results = res.scalars().all()
        # Создаем DataFrame из результатов запроса
        data = []
        for result in results:
            data.append({
                "number": result.number,
                "bank": result.bank.value,
                "typechanges": result.typechanges.value,
                "meta_data": result.meta_data,
                "link_new_file": result.link_new_file,
                "link_old_file": result.link_old_file,
                "link_compare_file": result.link_compare_file,
                "title": result.title,
                "description": result.description,
                "date": result.date
            })
        df = pd.DataFrame(data)
        # Записываем DataFrame в файл Excel
        file_path = "changes.xlsx"
        df.to_excel(file_path, index=False)
        with open(file_path, "rb") as file:
            await message.answer_document(file)


def register_handlers_commands(dp: Dispatcher):
    dp.register_message_handler(send_file, commands=['send_file'])
    dp.register_message_handler(export_excel, commands=['export_excel'])
    #dp.register_message_handler(commands_collector, IDFilter(collector_list), commands=['collector'])