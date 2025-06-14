import asyncio
import sys
import sqlite3
import json
import os
import subprocess
import psutil
import aiohttp
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from utils.utils_validation import validate_config, validate_block_schema
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

load_dotenv()
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
    try:
        c.execute('ALTER TABLE bot_configs ADD COLUMN bot_token TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('ALTER TABLE bot_configs ADD COLUMN pid INTEGER')
    except sqlite3.OperationalError:
        pass
    c.execute('SELECT config_id, pid FROM bot_configs WHERE pid IS NOT NULL')
    for config_id, pid in c.fetchall():
        try:
            process = psutil.Process(pid)
            process.terminate()
            process.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            pass
        c.execute('UPDATE bot_configs SET pid = NULL WHERE config_id = ?', (config_id,))
    conn.commit()
    conn.close()

dp = Dispatcher(storage=MemoryStorage())
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

class RegistrationForm(StatesGroup):
    name = State()
    confirm = State()

class BotCreationForm(StatesGroup):
    template = State()
    bot_name = State()
    bot_token = State()
    welcome_text = State()
    phone = State()
    email = State()
    website = State()
    help_text = State()

class FAQCreationForm(StatesGroup):
    faq_count = State()
    faq_question = State()
    faq_answer = State()
    more_faq = State()

class BotDeleteForm(StatesGroup):
    config_id = State()

@dp.message(Command("start"))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (message.from_user.id,))
    user = c.fetchone()
    conn.close()
    if user:
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
        await message.answer(
            "Привет! Добро пожаловать в билдер Telegram-ботов.\nВыберите действие:",
            reply_markup=keyboard
        )
    else:
        await message.answer("Привет! Давай зарегистрируем тебя. Введи свое имя:")
        await state.set_state(RegistrationForm.name)

def escape_markdown(text):
    """Escape special MarkdownV2 characters for Telegram."""
    if text is None:
        return ""
    special_chars = {
        '_': '\\_',
        '*': '\\*',
        '[': '\\[',
        ']': '\\]',
        '(': '\\(',
        ')': '\\)',
        '~': '\\~',
        '`': '\\`',
        '>': '\\>',
        '#': '\\#',
        '+': '\\+',
        '-': '\\-',
        '=': '\\=',
        '|': '\\|',
        '{': '\\{',
        '}': '\\}',
        '.': '\\.',
        '!': '\\!',
        '"': '\\"',
        "'": "\\'",
        "\\": "\\\\",
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
    }
    for char, escaped in special_chars.items():
        text = text.replace(char, escaped)
    return text

@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    await message.answer("Используйте /menu для управления ботами или /start для начала работы.")

@dp.message(Command("faq"))
async def command_faq_handler(message: Message) -> None:
    keyboard_buttons = [
        [
            InlineKeyboardButton(text="Что вы делаете?", callback_data="faq_what_do_you_do"),
            InlineKeyboardButton(text="Как связаться?", callback_data="faq_contact"),
        ],
        [
            InlineKeyboardButton(text="Где вы находитесь?", callback_data="faq_location"),
            InlineKeyboardButton(text="Вопрос 2", callback_data="faq_q2"),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await message.answer(
        "Часто задаваемые вопросы:\nВыберите интересующий вопрос.",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "faq_what_do_you_do")
async def callback_faq_what_do_you_do_handler(callback: CallbackQuery) -> None:
    await callback.message.answer("Мы создаем крутые Telegram-боты!")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "faq_contact")
async def callback_faq_contact_handler(callback: CallbackQuery) -> None:
    await callback.message.answer("Напишите на почту user@example.com или позвоните +1234567890.")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "faq_location")
async def callback_faq_location_handler(callback: CallbackQuery) -> None:
    await callback.message.answer("Наш офис находится в центре города.")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "faq_q2")
async def callback_faq_q2_handler(callback: CallbackQuery) -> None:
    await callback.message.answer("Ответ на вопрос 2")
    await callback.answer()

@dp.message(Command("create_bot"))
async def create_bot_handler(message: Message, state: FSMContext) -> None:
    keyboard_buttons = [
        [
            InlineKeyboardButton(text="Визитка", callback_data="template_business_card"),
            InlineKeyboardButton(text="FAQ", callback_data="template_faq"),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await message.answer("Выберите шаблон для нового бота:", reply_markup=keyboard)
    await state.set_state(BotCreationForm.template)

@dp.callback_query(lambda c: c.data.startswith("template_"))
async def process_template_selection(callback: CallbackQuery, state: FSMContext) -> None:
    template = callback.data.replace("template_", "")
    if template == "business_card":
        await state.update_data(template=template, config={"bot_name": "", "handlers": []})
        await callback.message.answer("Введите имя нового бота:")
        await state.set_state(BotCreationForm.bot_name)
    elif template == "faq":
        await state.update_data(template=template, config={"bot_name": "", "handlers": []}, faq_list=[])
        await callback.message.answer("Введите имя нового бота:")
        await state.set_state(BotCreationForm.bot_name)
    await callback.answer()

@dp.message(BotCreationForm.bot_name)
async def process_bot_name(message: Message, state: FSMContext) -> None:
    if message.text == "/cancel":
        await message.answer("Создание бота отменено.")
        await state.clear()
        return
    if not is_valid_text(message.text):
        await message.answer("Имя бота содержит недопустимые символы. Используйте буквы, цифры, пробелы и знаки препинания.")
        return
    await state.update_data(bot_name=message.text)
    user_data = await state.get_data()
    config = user_data['config']
    config['bot_name'] = message.text
    await state.update_data(config=config)
    await message.answer("Введите токен бота, полученный от @BotFather (или /cancel):")
    await state.set_state(BotCreationForm.bot_token)

@dp.message(BotCreationForm.bot_token)
async def process_bot_token(message: Message, state: FSMContext) -> None:
    if message.text == "/cancel":
        await message.answer("Создание бота отменено.")
        await state.clear()
        return
    bot_token = message.text.strip()
    if not bot_token.count(":") == 1 or not bot_token.split(":")[0].isdigit():
        await message.answer("Некорректный формат токена. Попробуйте снова или /cancel.")
        return
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.telegram.org/bot{bot_token}/getMe") as response:
            data = await response.json()
            if not data.get("ok"):
                await message.answer(f"Недействительный токен: {data.get('description', 'Ошибка')}. Попробуйте снова или /cancel.")
                return
    await state.update_data(bot_token=bot_token)
    template = (await state.get_data())['template']
    if template == "business_card":
        await message.answer("Введите текст приветствия для команды /start (или /skip для значения по умолчанию):")
        await state.set_state(BotCreationForm.welcome_text)
    elif template == "faq":
        await message.answer("Сколько вопросов FAQ вы хотите добавить? (1-4 или /cancel):")
        await state.set_state(FAQCreationForm.faq_count)

@dp.message(BotCreationForm.welcome_text)
async def process_welcome_text(message: Message, state: FSMContext) -> None:
    if message.text == "/cancel":
        await message.answer("Создание бота отменено.")
        await state.clear()
        return
    welcome_text = message.text if message.text != "/skip" else "Привет! Я бот-визитка.\nЗдесь вы можете найти всю необходимую информацию обо мне."
    if not is_valid_text(welcome_text):
        await message.answer("Текст приветствия содержит недопустимые символы. Используйте буквы, цифры, пробелы и знаки препинания.")
        return
    await state.update_data(welcome_text=welcome_text)
    await message.answer("Введите номер телефона (например, +1234567890) или /skip:")
    await state.set_state(BotCreationForm.phone)

@dp.message(BotCreationForm.phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    if message.text == "/cancel":
        await message.answer("Создание бота отменено.")
        await state.clear()
        return
    phone = message.text if message.text != "/skip" else None
    if phone:
        phone = phone.replace(" ", "").replace("tel:", "")
        if not phone.startswith("+") or not phone[1:].isdigit() or len(phone) < 7:
            await message.answer("Номер телефона должен начинаться с '+' и содержать только цифры (например, +79522046894). Минимум 6 цифр. Попробуйте снова или /skip.")
            return
    await state.update_data(phone=phone)
    await message.answer("Введите email (например, user@example.com) или /skip:")
    await state.set_state(BotCreationForm.email)

@dp.message(BotCreationForm.email)
async def process_email(message: Message, state: FSMContext) -> None:
    if message.text == "/cancel":
        await message.answer("Создание бота отменено.")
        await state.clear()
        return
    email = message.text if message.text != "/skip" else None
    if email and "@" not in email:
        await message.answer("Некорректный формат email. Попробуйте снова или /skip.")
        return
    await state.update_data(email=email)
    await message.answer("Введите URL сайта (например, https://example.com) или /skip:")
    await state.set_state(BotCreationForm.website)

@dp.message(BotCreationForm.website)
async def process_website(message: Message, state: FSMContext) -> None:
    if message.text == "/cancel":
        await message.answer("Создание бота отменено.")
        await state.clear()
        return
    website = message.text if message.text != "/skip" else None
    if website and not website.startswith(('http://', 'https://')):
        await message.answer("URL должен начинаться с http:// или https://. Попробуйте снова или /skip.")
        return
    await state.update_data(website=website)
    await message.answer("Введите текст для команды /help (или /skip для значения по умолчанию):")
    await state.set_state(BotCreationForm.help_text)

@dp.message(BotCreationForm.help_text)
async def process_help_text(message: Message, state: FSMContext) -> None:
    if message.text == "/cancel":
        await message.answer("Создание бота отменено.")
        await state.clear()
        return
    help_text = message.text if message.text != "/skip" else "Используйте /start для просмотра визитки."
    if not is_valid_text(help_text):
        await message.answer("Текст помощи содержит недопустимые символы. Используйте буквы, цифры, пробелы и знаки препинания.")
        return
    await state.update_data(help_text=help_text)
    await finalize_business_card(message, state)

def is_valid_text(text):
    """Validate text to ensure it contains only safe characters for Markdown and Python strings."""
    if not text:
        return False
    # Expanded allowed_chars to include Russian Cyrillic alphabet
    allowed_chars = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ,.!?+-*()[]{}:;@#$%^&_=<>~`" +
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    )
    return all(char in allowed_chars for char in text) and len(text.strip()) > 0

@dp.message(FAQCreationForm.faq_count)
async def process_faq_count(message: Message, state: FSMContext) -> None:
    if message.text == "/cancel":
        await message.answer("Создание бота отменено.")
        await state.clear()
        return
    try:
        faq_count = int(message.text)
        if faq_count < 1 or faq_count > 4:
            await message.answer("Число вопросов должно быть от 1 до 4. Попробуйте снова или /cancel.")
            return
        await state.update_data(faq_count=faq_count, current_faq=1)
        await message.answer("Введите текст первого вопроса FAQ:")
        await state.set_state(FAQCreationForm.faq_question)
    except ValueError:
        await message.answer("Ошибка: введите число или /cancel.")

@dp.message(FAQCreationForm.faq_question)
async def process_faq_question(message: Message, state: FSMContext) -> None:
    if message.text == "/cancel":
        await message.answer("Создание бота отменено.")
        await state.clear()
        return
    if not is_valid_text(message.text):
        await message.answer("Вопрос FAQ содержит недопустимые символы. Используйте буквы, цифры, пробелы и знаки препинания.")
        return
    await state.update_data(faq_question=message.text)
    await message.answer(f"Введите ответ на вопрос '{message.text}':")
    await state.set_state(FAQCreationForm.faq_answer)

@dp.message(FAQCreationForm.faq_answer)
async def process_faq_answer(message: Message, state: FSMContext) -> None:
    if message.text == "/cancel":
        await message.answer("Создание бота отменено.")
        await state.clear()
        return
    if not is_valid_text(message.text):
        await message.answer("Ответ FAQ содержит недопустимые символы. Используйте буквы, цифры, пробелы и знаки препинания.")
        return
    user_data = await state.get_data()
    faq_list = user_data.get('faq_list', [])
    faq_list.append({"question": user_data['faq_question'], "answer": message.text})
    await state.update_data(faq_list=faq_list)
    current_faq = user_data['current_faq']
    faq_count = user_data['faq_count']
    if current_faq < faq_count:
        await state.update_data(current_faq=current_faq + 1)
        await message.answer(f"Введите текст вопроса FAQ {current_faq + 1}:")
        await state.set_state(FAQCreationForm.faq_question)
    else:
        await finalize_faq(message, state)

async def finalize_business_card(message: Message, state: FSMContext):
    user_data = await state.get_data()
    config = user_data['config']
    bot_token = user_data['bot_token']
    welcome_text = escape_markdown(user_data['welcome_text'])
    phone = escape_markdown(user_data.get('phone'))
    email = escape_markdown(user_data.get('email'))
    website = escape_markdown(user_data.get('website'))
    help_text = escape_markdown(user_data['help_text'])

    contact_text = f"*{welcome_text}*\\n\\n📋 *Контактная информация:*\\n"
    if website:
        contact_text += f"🌐 *Website:* {website}\\n"
    if email:
        contact_text += f"📧 *Email:* {email}\\n"
    if phone:
        contact_text += f"📞 *Phone:* {phone}\\n"
    if not any([website, email, phone]):
        contact_text += "ℹ️ Контактная информация не указана.\\n"

    handlers = [
        {
            "command": "/start",
            "text": contact_text
        },
        {
            "command": "/help",
            "text": help_text
        },
        {
            "command": "/create_bot",
            "text": "Начать создание нового бота."
        },
        {
            "command": "/list_bots",
            "text": "Показать список ваших ботов."
        },
        {
            "command": "/delete_bot",
            "text": "Удалить бота."
        },
        {
            "command": "/menu",
            "text": "Выберите действие:",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {"text": "Создать бота", "callback_data": "menu_create_bot", "response": "Начнем создание бота!"},
                        {"text": "Список ботов", "callback_data": "menu_list_bots", "response": "Показываю ваши боты."}
                    ],
                    [
                        {"text": "Удалить бота", "callback_data": "menu_delete_bot", "response": "Выберите бота для удаления."}
                    ]
                ]
            }
        }
    ]

    config['handlers'] = handlers

    logger.debug(f"Business card config: {json.dumps(config, ensure_ascii=False)}")
    is_valid, error = validate_config(config)
    if not is_valid:
        await message.answer(f"Ошибка в конфигурации: {escape_markdown(str(error))}")
        await state.clear()
        return
    is_valid, error = validate_block_schema(config)
    if not is_valid:
        await message.answer(f"Ошибка в конфигурации: {escape_markdown(str(error))}")
        await state.clear()
        return

    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO bot_configs (user_id, bot_name, config_json, bot_token) VALUES (?, ?, ?, ?)',
        (message.from_user.id, config['bot_name'], json.dumps(config), bot_token)
    )
    config_id = c.lastrowid
    conn.commit()
    conn.close()

    try:
        await generate_and_run_bot(config, bot_token, config_id)
        await message.answer(f"Бот '{config['bot_name']}' успешно создан и запущен! ID: {config_id}")
    except Exception as e:
        logger.error(f"Error generating bot: {str(e)}")
        await message.answer(f"Ошибка при запуске бота: {escape_markdown(str(e))}")
    finally:
        await state.clear()

async def finalize_faq(message: Message, state: FSMContext):
    user_data = await state.get_data()
    config = user_data['config']
    bot_token = user_data['bot_token']
    faq_list = user_data.get('faq_list', [])

    faq_text = "Часто задаваемые вопросы:\\nВыберите интересующий вопрос\\."
    keyboard_buttons = []

    # Create serializable button data for config
    for i, faq in enumerate(faq_list, 1):
        callback_data = f"faq_{i}"
        keyboard_buttons.append([
            {
                "text": escape_markdown(faq['question']),
                "callback_data": callback_data,
                "response": escape_markdown(faq['answer'])
            }
        ])

    handlers = [
        {
            "command": "/start",
            "text": "Добро пожаловать в бот FAQ! Используйте /faq для просмотра вопросов."
        },
        {
            "command": "/faq",
            "text": faq_text,
            "reply_markup": {"inline_keyboard": keyboard_buttons}
        }
    ]

    config['handlers'] = handlers

    # Log the configuration
    try:
        logger.debug(f"FAQ config: {json.dumps(config, ensure_ascii=False)}")
    except Exception as e:
        logger.error(f"Failed to log config: {str(e)}")

    is_valid, error = validate_config(config)
    if not is_valid:
        logger.error(f"Config validation failed: {error}")
        await message.answer(f"Ошибка в конфигурации: {escape_markdown(str(error))}")
        await state.clear()
        return
    is_valid, error = validate_block_schema(config)
    if not is_valid:
        logger.error(f"Schema validation failed: {error}")
        await message.answer(f"Ошибка в конфигурации: {escape_markdown(str(error))}")
        await state.clear()
        return

    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO bot_configs (user_id, bot_name, config_json, bot_token) VALUES (?, ?, ?, ?)',
        (message.from_user.id, config['bot_name'], json.dumps(config), bot_token)
    )
    config_id = c.lastrowid
    conn.commit()
    conn.close()

    try:
        await generate_and_run_bot(config, bot_token, config_id)
        await message.answer(f"Бот '{config['bot_name']}' успешно создан и запущен! ID: {config_id}")
    except Exception as e:
        logger.error(f"Error generating bot: {str(e)}")
        await message.answer(f"Ошибка при запуске бота: {escape_markdown(str(e))}")
    finally:
        await state.clear()

async def generate_and_run_bot(config, bot_token, config_id):
    from generate import generate
    output_file = f"bots/bot_{config_id}.py"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    generate(config, output_file, config_id)
    env_file = f"bots/bot_{config_id}.env"
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(f"BOT_TOKEN={bot_token}\n")
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    c.execute('SELECT pid FROM bot_configs WHERE config_id = ?', (config_id,))
    result = c.fetchone()
    if result and result[0]:
        old_pid = result[0]
        try:
            old_process = psutil.Process(old_pid)
            old_process.terminate()
            old_process.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            pass
    process = subprocess.Popen(
        [sys.executable, os.path.abspath(output_file)],
        cwd=os.path.dirname(os.path.abspath(output_file)),
        env={**os.environ, "BOT_TOKEN": bot_token}
    )
    c.execute('UPDATE bot_configs SET pid = ? WHERE config_id = ?', (process.pid, config_id))
    conn.commit()
    conn.close()

@dp.message(Command("list_bots"))
async def list_bots_handler(message: Message) -> None:
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    c.execute('SELECT config_id, bot_name FROM bot_configs WHERE user_id = ?', (message.from_user.id,))
    bots = c.fetchall()
    conn.close()
    if bots:
        response = "Ваши боты:\n" + "\n".join([f"ID: {bot[0]}, Имя: {bot[1]}" for bot in bots])
    else:
        response = "У вас пока нет ботов."
    await message.answer(response)

@dp.message(Command("delete_bot"))
async def delete_bot_handler(message: Message, state: FSMContext) -> None:
    await message.answer("Введите ID бота для удаления (или /cancel):")
    await state.set_state(BotDeleteForm.config_id)

@dp.message(BotDeleteForm.config_id)
async def process_delete_id(message: Message, state: FSMContext) -> None:
    if message.text == "/cancel":
        await message.answer("Удаление отменено.")
        await state.clear()
        return
    try:
        config_id = int(message.text)
        conn = sqlite3.connect('bot_users.db')
        c = conn.cursor()
        c.execute('DELETE FROM bot_configs WHERE config_id = ? AND user_id = ?', 
                  (config_id, message.from_user.id))
        if c.rowcount > 0:
            await message.answer("Бот успешно удален!")
        else:
            await message.answer("Бот не найден или вы не владелец.")
        conn.commit()
        conn.close()
        await state.clear()
    except ValueError:
        await message.answer("Ошибка: ID должен быть числом.")
        await state.clear()

@dp.message(Command("menu"))
async def command_menu_handler(message: Message) -> None:
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
    await message.answer(
        "Выберите действие:",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "menu_create_bot")
async def callback_menu_create_bot_handler(callback: CallbackQuery, state: FSMContext) -> None:
    keyboard_buttons = [
        [
            InlineKeyboardButton(text="Визитка", callback_data="template_business_card"),
            InlineKeyboardButton(text="FAQ", callback_data="template_faq"),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.answer("Выберите шаблон для нового бота:", reply_markup=keyboard)
    await state.set_state(BotCreationForm.template)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "menu_list_bots")
async def callback_menu_list_bots_handler(callback: CallbackQuery) -> None:
    conn = sqlite3.connect('bot_users.db')
    c = conn.cursor()
    c.execute('SELECT config_id, bot_name FROM bot_configs WHERE user_id = ?', (callback.from_user.id,))
    bots = c.fetchall()
    conn.close()
    if bots:
        response = "Ваши боты:\n" + "\n".join([f"ID: {bot[0]}, Имя: {bot[1]}" for bot in bots])
    else:
        response = "У вас пока нет ботов."
    await callback.message.answer(response)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "menu_delete_bot")
async def callback_menu_delete_bot_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("Введите ID бота для удаления (или /cancel):")
    await state.set_state(BotDeleteForm.config_id)
    await callback.answer()

@dp.message(RegistrationForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    if not is_valid_text(message.text):
        await message.answer("Имя содержит недопустимые символы. Используйте буквы, цифры, пробелы и знаки препинания.")
        return
    await state.update_data(name=message.text)
    await message.answer(f"Ты ввел имя: {message.text}. Подтвердить? (да/нет)")
    await state.set_state(RegistrationForm.confirm)

@dp.message(RegistrationForm.confirm)
async def process_confirm(message: Message, state: FSMContext) -> None:
    if message.text.lower() == "да":
        user_data = await state.get_data()
        name = user_data['name']
        conn = sqlite3.connect('bot_users.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
                  (message.from_user.id, message.from_user.username, name))
        conn.commit()
        conn.close()
        await message.answer("Регистрация завершена! Нажми /start, чтобы продолжить.")
        await state.clear()
    else:
        await message.answer("Регистрация отменена! Нажми /start, чтобы начать заново.")
        await state.clear()

async def main() -> None:
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())