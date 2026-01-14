import os
import sys
import logging
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType

from settings import (
    VK_TOKEN,
    GOOGLE_APPLICATION_CREDENTIALS,
    TELEGRAM_TOKEN,
    ADMIN_CHAT_ID,
    PROJECT_ID,
)
import vk_handlers as vk_h
from logger import setup_logging


logger = logging.getLogger(__name__)


def handle_user_message_with_error_handling(event, vk_api, project_id):
    """Для обработки исключений при обработке сообщений пользователя"""
    try:
        vk_h.handle_user_message(event, vk_api, project_id)
    except Exception as err:
        logger.exception("Ошибка в VK обработчике")


def main():
    setup_logging(
        telegram_token=TELEGRAM_TOKEN, admin_chat_id=ADMIN_CHAT_ID, logger_instance=None
    )

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    vk_session = vk.VkApi(token=VK_TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    try:
        logger.info("VK бот запущен")
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                handle_user_message_with_error_handling(event, vk_api, PROJECT_ID)
    except KeyboardInterrupt:
        logger.warning("VK бот остановлен пользователем (Ctrl+C)")
        print("\nVK бот остановлен")
    except Exception as e:
        logger.exception("Непредвиденная ошибка в VK боте")
        raise


if __name__ == "__main__":
    main()
