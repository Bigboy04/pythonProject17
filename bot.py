from aiogram import Bot, Dispatcher

from aiogram.fsm.storage.memory import MemoryStorage

from config import API_TOKEN

bot = Bot(token=API_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
