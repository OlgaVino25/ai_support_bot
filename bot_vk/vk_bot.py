import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType

from settings import (
    VK_TOKEN,
    GOOGLE_APPLICATION_CREDENTIALS,
)
import vk_handlers as vk_h
from logger import logger


if __name__ == "__main__":
    logger.info("VK бот запущен")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    vk_session = vk.VkApi(token=VK_TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                vk_h.echo(event, vk_api)
    except KeyboardInterrupt:
        logger.warning("VK бот остановлен пользователем (Ctrl+C)")
        print("\nVK бот остановлен")
    except Exception as e:
        logger.exception("Непредвиденная ошибка в VK боте")
        raise
