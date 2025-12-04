import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command

from settings import (
    TELEGRAM_TOKEN,
    ADMIN_CHAT_ID,
    GOOGLE_APPLICATION_CREDENTIALS,
)
from bot_tg import tg_handlers as tg_h
from logger import setup_logging


async def main():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    logger = setup_logging(bot, ADMIN_CHAT_ID)

    dp.message.register(tg_h.start, Command(commands=["start"]))
    dp.message.register(tg_h.echo)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Бот запущен. Для обучения DialogFlow запустите отдельно train_dialogflow.py")
    asyncio.run(main())
