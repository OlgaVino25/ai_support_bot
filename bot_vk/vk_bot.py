import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
import logging
from aiogram import Bot

from settings import (
    VK_TOKEN,
    GOOGLE_APPLICATION_CREDENTIALS,
    TELEGRAM_TOKEN,
    ADMIN_CHAT_ID,
)
from bot_vk import vk_handlers as vk_h
from logger import setup_logging


if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    telegram_bot = Bot(token=TELEGRAM_TOKEN)
    setup_logging(telegram_bot, ADMIN_CHAT_ID)

    logger = logging.getLogger(__name__)
    logger.info("VK бот запущен")

    vk_session = vk.VkApi(token=VK_TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    print("Бот запущен. Для обучения DialogFlow запустите отдельно train_dialogflow.py")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            vk_h.echo(event, vk_api)
