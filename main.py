import asyncio
import os
import configparser
import logging
import sentry_sdk

from fastapi import FastAPI, status, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from banks.common_func.notification import notification_text_daily, List_notification
from db.core import AsyncORM
from banks.main_job import execute_once_daily, test_execute_once_daily
from bot_tg.create_bot import dp, bot, scheduler
from aiogram import types, Dispatcher, Bot


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
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
py_handler.setFormatter(py_formatter)
# добавление обработчика к логгеру
py_logger.addHandler(py_handler)


# url для webhook
# Создайте экземпляр ConfigParser
config = configparser.ConfigParser()

# Прочитайте файл конфигурации
config.read('.env')

# Получите значения из файла конфигурации
NGROK_TUNNEL_URL = config.get('Settings', 'NGROK_TUNNEL_URL')
TELEGRAM_BOT_TOKENT = config.get('Settings', 'bot_token')

WEBHOOK_PATH = f"/bot/{TELEGRAM_BOT_TOKENT}"
WEBHOOK_URL = f"{NGROK_TUNNEL_URL}{WEBHOOK_PATH}"


async def my_async_function():
    # Ваша асинхронная функция, которую нужно выполнить каждую минуту
    py_logger.debug("Асинхронная функция выполняется!")


@app.on_event("startup")
async def on_startup():
    # настройки для бота
    webhook_info = await bot.get_webhook_info()
    py_logger.info(f"webhook_info: {webhook_info}")
    if webhook_info.url != WEBHOOK_URL:
        set_webhook = await bot.set_webhook(url=WEBHOOK_URL)
        py_logger.info(f"set_webhook: {set_webhook}")

    # запускаем базу данных
    await AsyncORM.create_tables()
    #asyncio.create_task(execute_once_daily())

    # Добавляем задачу, которая будет выполняться каждую минуту и запускаем планировщик
    scheduler.add_job(my_async_function, 'interval', minutes=1)
    scheduler.add_job(my_async_function, 'cron', hour=0, minute=53)
    scheduler.start()

    py_logger.info(f"Bot online {__name__}...")


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    py_logger.debug(f"update: {update}")
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)
    py_logger.debug(f"Update: {telegram_update}  {__name__}...")
    return 200, "ok"


app.mount("/banks", StaticFiles(directory="banks"), name="banks")
templates = Jinja2Templates(directory="banks")


@app.get("/get_compare_html/{bank}/{file_name}", response_class=HTMLResponse)
async def read_item(request: Request, bank: str, file_name: str):
    try:
        return templates.TemplateResponse(f"/{bank}/data/{file_name}", {"request": request, "bank": bank})
    except:
        raise HTTPException(status_code=400, detail="Файл не существует")


@app.post("/notification_daily/", response_model=List_notification, status_code=status.HTTP_200_OK)
async def notification_daily():
    # Возвращаем объект List_notification в виде JSON
    data_for_return = await notification_text_daily()
    return data_for_return


@app.get("/get_file/{bank}/{file_name}", response_class=FileResponse)
async def read_item(bank: str, file_name: str):
    file_path = f"{os.getcwd()}/banks/{bank}/data/{file_name}"

    if not os.path.exists(file_path):
        file_path = f"{os.getcwd()}/banks/{bank}/{file_name}"

        if not os.path.exists(file_path):
            print(file_path)
            raise HTTPException(status_code=400, detail="Файл не существует")
        else:
            return FileResponse(file_path)

    return FileResponse(file_path)


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()
    py_logger.info(f"Bot offline {__name__}...")


async def startup_test():
    await AsyncORM.create_tables()
    #await execute_once_daily()
    #await test_execute_once_daily()
    await execute_once_daily()
    #await notification_text_daily()


if __name__ == '__main__':
    asyncio.run(startup_test())
