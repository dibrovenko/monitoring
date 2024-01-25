import asyncio
import os
#from dotenv import load_dotenv, find_dotenv
import dotenv
import logging
from fastapi import FastAPI
import sentry_sdk

from bot_tg.create_bot import dp, bot, scheduler
from aiogram import types, Dispatcher, Bot
from db.core import AsyncORM


sentry_sdk.init(
  dsn="https://7545c747e68a60a25d8634ac9a82ed4e@o4505706547314688.ingest.sentry.io/4505710368063488",

  # Set traces_sample_rate to 1.0 to capture 100%
  # of transactions for performance monitoring.
  # We recommend adjusting this value in production.
  traces_sample_rate=1.0
)

app = FastAPI()

# получение пользовательского логгера и установка уровня логирования
py_logger = logging.getLogger(__name__)
py_logger.setLevel(logging.DEBUG)

# настройка обработчика и форматировщика в соответствии с нашими нуждами
log_file = os.path.join(f"log_directory/{__name__}.log")
py_handler = logging.FileHandler(log_file, mode='w')

#py_handler = logging.FileHandler(f"{__name__}.log", mode='w')
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
py_handler.setFormatter(py_formatter)
# добавление обработчика к логгеру
py_logger.addHandler(py_handler)


# url для webhook
load_dotenv(find_dotenv())
NGROK_TUNNEL_URL = os.getenv('NGROK_TUNNEL_URL')
TELEGRAM_BOT_TOKENT = os.getenv('bot_token')

WEBHOOK_PATH = f"/bot/{TELEGRAM_BOT_TOKENT}"
WEBHOOK_URL = f"{NGROK_TUNNEL_URL}{WEBHOOK_PATH}"


@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    py_logger.info(f"webhook_info: {webhook_info}")
    if webhook_info.url != WEBHOOK_URL:
        set_webhook = await bot.set_webhook(url=WEBHOOK_URL)
        py_logger.info(f"set_webhook: {set_webhook}")
    await AsyncORM.create_tables()
    scheduler.start()
    py_logger.info(f"Bot online {__name__}...")


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)
    py_logger.debug(f"Update: {telegram_update}  {__name__}...")


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()
    py_logger.info(f"Bot offline {__name__}...")



"""import asyncio
from banks.main_job import execute_once_daily
from db.core import AsyncORM
from db.models import Changes, Banks, TypeChanges


async def startup():
    await AsyncORM.create_tables()
    await execute_once_daily()

if __name__ == '__main__':
    asyncio.run(startup())
    #loop.run_until_complete(execute_once_daily())
    uvicorn main:app
"""