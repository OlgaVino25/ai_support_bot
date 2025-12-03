import random

from environs import Env

from google.cloud import dialogflow


env = Env()
env.read_env()

project_id = env.str("PROJECT_ID")


def echo(event, vk_api):
    """Обработка сообщений VK с использованием DialogFlow"""
    try:
        user_id = event.user_id if event.user_id != 0 else event.peer_id
        session_id = f"vk-{user_id}"

        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, session_id)

        text_input = dialogflow.TextInput(text=event.text, language_code="ru")
        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        dialogflow_response = response.query_result.fulfillment_text

        vk_api.messages.send(
            user_id=event.user_id,
            message=dialogflow_response,
            random_id=random.randint(1, 1000),
        )
    except Exception as e:
        print(f"Error in VK handler: {e}")
        vk_api.messages.send(
            user_id=event.user_id,
            message="Извините, произошла ошибка при обработке вашего сообщения.",
            random_id=random.randint(1, 1000),
        )
