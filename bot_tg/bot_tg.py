from environs import Env
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from google.cloud import dialogflow
import asyncio

import handlers as h


env = Env()
env.read_env()

token = env.str("CONTEXT_ASSISTANT_BOT_TG_TOKEN")
project_id = env.str("PROJECT_ID")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env.str(
    "GOOGLE_APPLICATION_CREDENTIALS", "credentials.json"
)


bot = Bot(token=token)

dp = Dispatcher()


dp.message.register(h.start, Command(commands=["start"]))
dp.message.register(h.echo)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
