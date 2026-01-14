import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import logging

from aiogram import types
from google.cloud import dialogflow


logger = logging.getLogger(__name__)


async def start(message: types.Message):
    await message.answer(
        "Здравствуйте! Я бот с искусственным интеллектом. Задавайте вопросы!"
    )


async def echo(message, project_id):

    user_text = message.text
    user_id = message.from_user.id

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, f"tg-{user_id}")

    text_input = dialogflow.TextInput(text=user_text, language_code="ru")
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    bot_response = response.query_result.fulfillment_text

    await message.answer(bot_response)
