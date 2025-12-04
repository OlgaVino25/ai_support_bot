import random
import logging

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from google.cloud import dialogflow

from settings import PROJECT_ID


logger = logging.getLogger(__name__)


def echo(event, vk_api):
    """Обработка сообщений VK с использованием DialogFlow"""
    try:
        user_id = event.user_id if event.user_id != 0 else event.peer_id
        session_id = f"vk-{user_id}"

        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(PROJECT_ID, session_id)

        text_input = dialogflow.TextInput(text=event.text, language_code="ru")
        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        if response.query_result.intent.is_fallback:
            return

        dialogflow_response = response.query_result.fulfillment_text

        vk_api.messages.send(
            user_id=event.user_id,
            message=dialogflow_response,
            random_id=random.randint(1, 1000),
        )
    except Exception as e:
        logger.error(f"Error in VK handler: {e}")
        try:
            vk_api.messages.send(
                user_id=event.user_id,
                message="Извините, произошла ошибка при обработке вашего сообщения.",
                random_id=random.randint(1, 1000),
            )
        except Exception as send_error:
            logger.error(f"Не удалось отправить сообщение об ошибке: {send_error}")
