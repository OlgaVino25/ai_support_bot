from aiogram import types
from aiogram.filters import Command


async def start(message: types.Message):
    await message.answer("Здравствуйте!")


async def echo(message: types.Message):
    await message.answer(message.text)
