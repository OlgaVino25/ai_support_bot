import asyncio
import os
import sys
from pathlib import Path

from environs import Env
from aiogram import Bot, Dispatcher
from aiogram.filters import Command

import tg_handlers as tg_h


BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR))


async def main():
    env = Env()
    env.read_env()

    tg_token = env.str("CONTEXT_ASSISTANT_BOT_TG_TOKEN")

    credentials_path = BASE_DIR / "credentials.json"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)

    bot = Bot(token=tg_token)
    dp = Dispatcher()

    dp.message.register(tg_h.start, Command(commands=["start"]))
    dp.message.register(tg_h.echo)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Бот запущен. Для обучения DialogFlow запустите отдельно train_dialogflow.py")
    asyncio.run(main())
