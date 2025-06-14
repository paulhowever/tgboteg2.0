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

env_path = os.path.join(os.path.dirname(__file__), "bot_7.env")
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
    
    await message.answer("Добро пожаловать в бот FAQ! Используйте /faq для просмотра вопросов.")
    





@dp.callback_query(lambda c: c.data == "faq_1")
async def callback_faq_1_handler(callback: CallbackQuery) -> None:
    try:
        await callback.message.answer("asdfasdfadfsadfs")
        await callback.answer()
    except Exception as e:
        await callback.answer(text=f"Error occurred: {str(e)}")




@dp.message(Command("faq"))
async def faq_handler(message: Message) -> None:
    
    keyboard_buttons = [
        
        [
            
            
            InlineKeyboardButton(text="asdfasdfadsf", callback_data="faq_1"),
            
            
        ],
        
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await message.answer("Часто задаваемые вопросы:\nВыберите интересующий вопрос\.", reply_markup=keyboard)
    






@dp.message(Command("start"))
async def start_handler(message: Message) -> None:
    
    await message.answer("Добро пожаловать в бот FAQ! Используйте /faq для просмотра вопросов.", parse_mode=ParseMode.MARKDOWN)
    





@dp.callback_query(lambda c: c.data == "faq_1")
async def callback_faq_1_handler(callback: CallbackQuery) -> None:
    try:
        await callback.message.answer("asdfasdfadfsadfs")
        await callback.answer()
    except Exception as e:
        await callback.answer(text=f"Error occurred: {str(e)}")




@dp.message(Command("faq"))
async def faq_handler(message: Message) -> None:
    
    keyboard_buttons = [
        
        [
            
            
            InlineKeyboardButton(text="asdfasdfadsf", callback_data="faq_1"),
            
            
        ],
        
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await message.answer("Часто задаваемые вопросы:\nВыберите интересующий вопрос\.", reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
    


@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    help_text = "*Для помощи напишите администратору:* @NeK0TeR"
    await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)



async def main() -> None:
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())