import os
import configparser

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
storage = MemoryStorage()

# Создайте экземпляр ConfigParser
config = configparser.ConfigParser()
# Прочитайте файл конфигурации
config.read('.env')
bot = Bot(token=config.get('Settings', 'bot_token'))
dp = Dispatcher(bot=bot, storage=storage, run_tasks_by_default=True)


from bot_tg.handlers import start, commands, filter, errors
filter.register_handlers_filter(dp)
commands.register_handlers_commands(dp)
start.register_handlers_start(dp)
errors.register_handlers_error(dp)  # ниже всех


