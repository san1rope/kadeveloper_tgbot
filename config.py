import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN").strip()
    BOT = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    DISPATCHER = Dispatcher(storage=MemoryStorage())
    API_URL = os.getenv("API_URL").strip()

    DATABASE_CLEANUP = bool(int(os.getenv("DATABASE_CLEANUP")))
    DB_USER = os.getenv("DB_USER").strip()
    DB_PASSWORD = os.getenv("DB_PASSWORD").strip()
    DB_HOST = os.getenv("DB_HOST").strip()
    DB_NAME = os.getenv("DB_NAME").strip()
