import asyncio
import logging
from aiogram import Bot
from typing import Optional


class TelegramLogsHandler(logging.Handler):
    """Кастомный обработчик для отправки логов в Telegram"""

    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def emit(self, record):
        log_entry = self.format(record)

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            asyncio.create_task(self._send_log_async(log_entry))
        else:
            loop.run_until_complete(self._send_log_async(log_entry))

    async def _send_log_async(self, message: str):
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message[:4000])
        except Exception as e:
            print(f"Не удалось отправить лог в Telegram: {e}")
            print(f"Текст лога: {message[:500]}")


def setup_logging(bot, admin_chat_id):
    """Настраивает систему логирования"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.handlers.clear()

    # Обработчик для Telegram
    telegram_handler = TelegramLogsHandler(bot, admin_chat_id)
    telegram_handler.setLevel(logging.WARNING)
    telegram_formatter = logging.Formatter(
        "*%(levelname)s*\n\n"
        "*Сообщение*: %(message)s\n"
        "*Время*: %(asctime)s\n"
        "*Файл*: %(filename)s\n"
        "*Строка*: %(lineno)d\n"
        "*Модуль*: %(module)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    telegram_handler.setFormatter(telegram_formatter)
    logger.addHandler(telegram_handler)

    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Логирование для библиотек
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("vk_api").setLevel(logging.WARNING)

    return logger
