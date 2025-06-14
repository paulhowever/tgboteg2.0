import asyncio
import sys
import sqlite3
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from utils.utils_validation import validate_config

env_path = os.path.join(os.path.dirname(__file__), "bot_3.env")
load_dotenv(env_path)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

def init_db():
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS bot_configs (
            config_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            bot_name TEXT,
            config_json TEXT,
            bot_token TEXT,
            pid INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    conn.commit()
    conn.close()

dp = Dispatcher()
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))



@dp.message(Command("start"))
async def start_handler(message: Message) -> None:
    
    await message.answer("*asdfadsf*\n\n📋 *Контактная информация:*\nℹ️ Контактная информация не указана.\n")
    


@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    
    await message.answer("dsaf")
    


@dp.message(Command("create_bot"))
async def create_bot_handler(message: Message) -> None:
    
    await message.answer("Начать создание нового бота.")
    


@dp.message(Command("list_bots"))
async def list_bots_handler(message: Message) -> None:
    
    await message.answer("Показать список ваших ботов.")
    


@dp.message(Command("delete_bot"))
async def delete_bot_handler(message: Message) -> None:
    
    await message.answer("Удалить бота.")
    





@dp.callback_query(lambda c: c.data == "menu_create_bot")
async def callback_menu_create_bot_handler(callback: CallbackQuery) -> None:
    try:
        await callback.message.answer("Начнем создание бота!")
        await callback.answer()
    except Exception as e:
        await callback.answer(text=f"Error occurred: {str(e)}")



@dp.callback_query(lambda c: c.data == "menu_list_bots")
async def callback_menu_list_bots_handler(callback: CallbackQuery) -> None:
    try:
        await callback.message.answer("Показываю ваши боты.")
        await callback.answer()
    except Exception as e:
        await callback.answer(text=f"Error occurred: {str(e)}")





@dp.callback_query(lambda c: c.data == "menu_delete_bot")
async def callback_menu_delete_bot_handler(callback: CallbackQuery) -> None:
    try:
        await callback.message.answer("Выберите бота для удаления.")
        await callback.answer()
    except Exception as e:
        await callback.answer(text=f"Error occurred: {str(e)}")




@dp.message(Command("menu"))
async def menu_handler(message: Message) -> None:
    
    keyboard_buttons = [
        
        [
            
            
            InlineKeyboardButton(text="Создать бота", callback_data="menu_create_bot"),
            
            
            
            InlineKeyboardButton(text="Список ботов", callback_data="menu_list_bots"),
            
            
        ],
        
        [
            
            
            InlineKeyboardButton(text="Удалить бота", callback_data="menu_delete_bot"),
            
            
        ],
        
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await message.answer("Выберите действие:", reply_markup=keyboard)
    


async def main() -> None:
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())