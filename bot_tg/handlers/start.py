from bot_tg.create_bot import dp, bot
from aiogram import types, Dispatcher
from aiogram.types import BotCommandScopeChat, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, \
    KeyboardButton


async def set_commands():
    bot_commands = [
        types.BotCommand(command="/start", description="перезапустить бота"),
        types.BotCommand(command="/help", description="подсказки"),
        types.BotCommand(command="/get_file ", description="получить файл по ссылке"),
        types.BotCommand(command="/send_file", description="отправить базу данных"),
        types.BotCommand(command="/export_excel", description="экспортировать данные в Excel")
    ]
    await bot.set_my_commands(bot_commands)


# Определяем обработчик команды /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await set_commands()
    # Приветственное сообщение
    welcome_message = (
        "Привет! Я бот, который поможет тебе отслеживать изменения в банках конкурентов. "
    )
    await bot.send_sticker(chat_id=message.chat.id,
                           sticker=r"CAACAgIAAxkBAAELSJRluVE-y4WlFi2KiCTYAShwktb2hQACVhgAAtk-GUhnGFQ1T6HUWjQE")
    await message.answer(welcome_message, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton("Посмотреть историю изменений")
    ))


# Определяем обработчик команды /help
@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    # Описание доступных команд
    help_message = (
        "Я бот, который отслеживает изменения в банках конкурентов. "
        "Вот список доступных команд:\n\n"
        "/start - перезапустить бота\n"
        "/help - подсказки\n"
        "/get_file - получить файл с изменениями\n"
        "/send_file - отправить базу данных\n"
        "/export_excel - экспортировать данные в Excel"
    )
    await message.answer(help_message)


def register_handlers_start(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(cmd_help, commands=['help'])
