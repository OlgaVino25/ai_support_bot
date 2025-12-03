from environs import Env
from aiogram import types
from google.cloud import dialogflow


env = Env()
env.read_env()

project_id = env.str("PROJECT_ID")


async def start(message: types.Message):
    await message.answer(
        "Здравствуйте! Я бот с искусственным интеллектом. Задавайте вопросы!"
    )


async def echo(message: types.Message):
    try:
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

    except Exception as e:
        print(f"Error: {e}")
        await message.answer(
            "Извините, произошла ошибка при обработке вашего сообщения."
        )
