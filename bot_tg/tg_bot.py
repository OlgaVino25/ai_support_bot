import asyncio
import os

from environs import Env
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from google.cloud import dialogflow

import tg_handlers as tg_h


env = Env()
env.read_env()

token = env.str("CONTEXT_ASSISTANT_BOT_TG_TOKEN")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env.str(
    "GOOGLE_APPLICATION_CREDENTIALS", "credentials.json"
)


bot = Bot(token=token)
dp = Dispatcher()

dp.message.register(tg_h.start, Command(commands=["start"]))
dp.message.register(tg_h.echo)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Бот запущен. Для обучения DialogFlow запустите отдельно train_dialogflow.py")
    asyncio.run(main())
