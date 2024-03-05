import os

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, MediaGroup, \
    InputFile
from typing import List, Type


from db.core import AsyncORM
from db.schemas import ChangesFULLDTO

from bot_tg.create_bot import dp, bot
from db.models import Changes, Banks, TypeChanges


class File(StatesGroup):
    link = State()


# @dp.message_handler(commands=['get_file'], state="*")
async def get_file(message: types.Message, state: FSMContext):
    await message.answer("Вы можете просмотреть нужную ссылку в базе данных, скопировать ее и отправить сюда в "
                         "следующем формате: /Users/paveldibrovenko/Desktop/Tink_mon/monitoring/banks/tochka/data.",
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                             KeyboardButton(f"отмена ✕")))
    await File.link.set()


class Form(StatesGroup):
    bank = State()
    type_changes = State()


# @dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Нажми на кнопку, чтобы посмотреть историю изменений",
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                             KeyboardButton(f"Посмотреть историю изменений")))


# @dp.message_handlerr(state=File.link)
async def catch_link(message: types.Message, state: FSMContext):
    if os.path.isfile(message.text):
        await message.answer_document(InputFile(message.text))
    else:
        await bot.send_sticker(chat_id=message.chat.id,
                               sticker=r"CAACAgIAAxkBAAELSJBluVEyRX16WxIURrjniGCuniyOPAAC8RgAAh8oGUgCDaF-Lcl_RTQE")
        await message.answer("Файла такого не сущетсвует",
                             reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                 KeyboardButton(f"Посмотреть историю изменений")))
    await state.finish()


# @dp.message_handler(lambda message: message.text == "Посмотреть историю изменений", state="*")
async def start_form(message: types.Message, state: FSMContext):
    await message.reply("хорошо", reply=message.message_id,
                        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(f"отмена ✕")))
    await Form.bank.set()
    banks_keyboard = InlineKeyboardMarkup(row_width=1)
    for bank in Banks:
        banks_keyboard.add(InlineKeyboardButton(text=bank.value, callback_data=f"bank_{bank.name}"))
    await message.answer("Выберите банк:", reply_markup=banks_keyboard)


# @dp.callback_query_handler(lambda c: c.data.startswith('bank_'), state=Form.bank)
async def process_bank(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['bank'] = callback_query.data[5:]
    await Form.next()
    type_changes_keyboard = InlineKeyboardMarkup(row_width=1)
    for change_type in TypeChanges:
        type_changes_keyboard.add(
            InlineKeyboardButton(text=change_type.value, callback_data=f"type_{change_type.name}"))
    await callback_query.message.answer("Выберите тип изменений:", reply_markup=type_changes_keyboard)



# @dp.callback_query_handler(lambda c: c.data.startswith('type_'), state=Form.type_changes)
async def process_type(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        bank = data['bank']
    type_changes = callback_query.data[5:]
    changes_from_db: List[ChangesFULLDTO] = await AsyncORM.select_changes_for_compare(bank=bank,
                                                                                      typechanges=type_changes)

    for change in changes_from_db:
        text = f"Номер: {change.number}\n" \
               f"Банк: {str(change.bank)[6:]}\n" \
               f"Тип изменения: {str(change.typechanges)[12:]}\n" \
               f"Заголовок: {change.title}\n" \
               f"Описание: {change.description}\n"
        await callback_query.message.answer(text=text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                 KeyboardButton(f"Посмотреть историю изменений")))

        album = MediaGroup()
        if change.link_new_file is not None and os.path.isfile(change.link_new_file):
            album.attach_document(document=InputFile(path_or_bytesio=change.link_new_file), caption="new")
        if change.link_old_file is not None and os.path.isfile(change.link_old_file):
            album.attach_document(document=InputFile(path_or_bytesio=change.link_old_file), caption="old")
        if change.link_compare_file is not None and os.path.isfile(change.link_compare_file):
            album.attach_document(document=InputFile(path_or_bytesio=change.link_compare_file), caption="compare")
        await callback_query.message.answer_media_group(media=album)

    if not changes_from_db:
        await bot.send_sticker(chat_id=callback_query.message.chat.id,
                               sticker=r"CAACAgIAAxkBAAELSJBluVEyRX16WxIURrjniGCuniyOPAAC8RgAAh8oGUgCDaF-Lcl_RTQE")
        await callback_query.message.answer(text="Данный параметр пока не добавлен",
                                            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                                                KeyboardButton(f"Посмотреть историю изменений")))
        await state.finish()


# @dp.message_handler(filters.Text(equals='отмена ✕', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    await message.reply('ок', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).
                        add(KeyboardButton(f"Посмотреть историю изменений")))
    await state.finish()


def register_handlers_filter(dp: Dispatcher):
    dp.register_message_handler(cancel_handler, filters.Text(equals='отмена ✕', ignore_case=True), state="*")
    dp.register_message_handler(start_form, lambda message: message.text == "Посмотреть историю изменений", state="*")
    dp.register_callback_query_handler(process_bank, lambda c: c.data.startswith('bank_'), state=Form.bank)
    dp.register_callback_query_handler(process_type, lambda c: c.data.startswith('type_'), state=Form.type_changes)

    dp.register_message_handler(get_file, commands=['get_file'], state="*")
    dp.register_message_handler(catch_link, state=File.link)
