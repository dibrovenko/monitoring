import asyncio
import random
import time
import logging
import os

from aiogram.dispatcher import FSMContext
from bot_tg.create_bot import dp, bot
from aiogram import types, Dispatcher
from aiogram.types import BotCommandScopeChat, InlineKeyboardButton, InlineKeyboardMarkup

# получение пользовательского логгера и установка уровня логирования
py_logger = logging.getLogger(__name__)
py_logger.setLevel(logging.INFO)

# настройка обработчика и форматировщика в соответствии с нашими нуждами
log_file = os.path.join(f"log_directory/{__name__}.log")
py_handler = logging.FileHandler(log_file, mode='w')

#py_handler = logging.FileHandler(f"{__name__}.log", mode='w')
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
py_handler.setFormatter(py_formatter)
# добавление обработчика к логгеру
py_logger.addHandler(py_handler)


#@dp.message_handler()
async def echo_send(message: types.Message):
    if message.text == "Привет":
        await asyncio.sleep(5)
        await message.answer(message.from_user.id)
    elif message.text == "инфа":
        await message.answer(message.text)
    else:
        await message.answer(message.text)

    await bot.send_message(chat_id=message.chat.id, text="именно бот")
    #await message.reply(message.text)
    #await bot.send_message(message.from_user.id, message.text)


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(echo_send)


async def delete_messages(chat_id, start, end, time: float, time_circle: float):
    """
    Удаляет промежуток сообщений за нужное время
    :param chat_id:
    :param start:
    :param end:
    :param time:
    :param time_circle:
    """
    await asyncio.sleep(time)
    for i in range(start, end):
        try:
            await asyncio.sleep(time_circle)
            await bot.delete_message(chat_id=chat_id, message_id=i)
        except:
            pass


async def set_admin_commands(message: types.Message):
    bot_commands = [
        types.BotCommand(command="/start", description="перезапустить бота"),
        types.BotCommand(command="/client", description="клиенский интерфейс"),
        types.BotCommand(command="/collector", description="интерфейс сборщика"),
        types.BotCommand(command="/record_goods_excel", description="изменить данные товаров с Exel"),
        types.BotCommand(command="/take_goods_excel", description="получить данные товаров с Exel"),
        types.BotCommand(command="/take_orders_excel", description="получить данные о заказах с Exel")
    ]
    scope = BotCommandScopeChat(chat_id=message.chat.id)
    await bot.set_my_commands(bot_commands, scope=scope)


async def set_collectors_commands(message: types.Message):
    bot_commands = [
        types.BotCommand(command="/start", description="перезапустить бота"),
        types.BotCommand(command="/client", description="клиенский интерфейс"),
        types.BotCommand(command="/admin", description="admin интерфейс"),
        types.BotCommand(command="/take_orders_excel", description="получить данные о заказах с Exel")
    ]
    scope = BotCommandScopeChat(chat_id=message.chat.id)
    await bot.set_my_commands(bot_commands, scope=scope)


async def set_client_commands():
    bot_commands = [
        types.BotCommand(command="/start", description="перезапустить бота"),
        types.BotCommand(command="/help", description="подсказки"),
        types.BotCommand(command="/info", description="получить информацию")
    ]
    await bot.set_my_commands(bot_commands)


async def set_client_commands2(message: types.Message):
    bot_commands = [
        types.BotCommand(command="/start", description="перезапустить бота"),
        types.BotCommand(command="/admin", description="admin интерфейс"),
        types.BotCommand(command="/collector", description="интерфейс сборщика"),
    ]
    scope = BotCommandScopeChat(chat_id=message.chat.id)
    await bot.set_my_commands(bot_commands, scope=scope)

