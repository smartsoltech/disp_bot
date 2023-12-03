import asyncio
import logging
import os
import sys
from aiogram.types import BotCommand
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
import db
import func
from dotenv import load_dotenv
from icecream import ic

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
router = Router()

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    user_lang = await db.get_user_language(message.from_user.id)
    welcome_text = func.get_text(user_lang, 'welcome')
    await message.answer(welcome_text)

@dp.message_handler(commands=['language'])
async def change_language(message: types.Message):
    # Реализация функции для изменения языка пользователя
    pass

@dp.message_handler(lambda message: message.text in ["Новые заявки", "В работе", "Завершенные"])
async def show_issues_by_status(message: types.Message):
    status = db.IssueStatus.NEW if message.text == "Новые заявки" \
        else db.IssueStatus.IN_PROGRESS if message.text == "В работе" \
        else db.IssueStatus.RESOLVED
    issues = await db.get_issues_by_status(status)
    # Отображение заявок пользователю
    pass

@dp.callback_query_handler(lambda call: True)
async def callback_query_handler(call: types.CallbackQuery):
    # Обработка нажатий на кнопки инлайн-клавиатуры
    pass

async def on_startup(dp):
    await db.database.connect()
    await db.init_db()  # Инициализация базы данных

async def on_shutdown(dp):
    await db.database.disconnect()

async def main():
    # Инициализация Bot и Dispatcher
    await dp.start_polling(bot, on_startup=on_startup, on_shutdown=on_shutdown)
    
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())