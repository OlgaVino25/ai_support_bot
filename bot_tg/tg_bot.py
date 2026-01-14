import os
import sys
import logging
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command

from settings import (
    TELEGRAM_TOKEN,
    GOOGLE_APPLICATION_CREDENTIALS,
)
import tg_handlers as tg_h
from logger import setup_logging


logger = logging.getLogger(__name__)


async def main():
    setup_logging(logger)
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()

    dp.message.register(tg_h.start, Command(commands=["start"]))
    dp.message.register(tg_h.echo)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception("Непредвиденная ошибка в Telegram боте")
        raise


if __name__ == "__main__":
    logger.info("Бот запущен")
    asyncio.run(main())
