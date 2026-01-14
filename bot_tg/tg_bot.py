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
    ADMIN_CHAT_ID,
    PROJECT_ID,
)
import tg_handlers as tg_h
from logger import setup_logging


logger = logging.getLogger(__name__)


async def echo_wrapper(message):
    await tg_h.echo(message, PROJECT_ID)


async def main():
    setup_logging(
        telegram_token=TELEGRAM_TOKEN,
        admin_chat_id=ADMIN_CHAT_ID,
        logger_instance=None
    )

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()

    dp.message.register(tg_h.start, Command(commands=["start"]))
    dp.message.register(echo_wrapper)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception("Непредвиденная ошибка в Telegram боте")
        raise


if __name__ == "__main__":
    logger.info("Бот запущен")
    asyncio.run(main())
