from environs import Env

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
import asyncio

import handlers as h


env = Env()
env.read_env()

token = env.str("CONTEXT_ASSISTANT_BOT_TG_TOKEN")

bot = Bot(token=token)

dp = Dispatcher()

dp.message.register(h.start, Command(commands=["start"]))
dp.message.register(h.echo)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
