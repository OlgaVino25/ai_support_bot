import os
import sys
import logging
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import json
import asyncio
from google.cloud import dialogflow

from settings import (
    PHRASES_PATH,
    PROJECT_ID,
    GOOGLE_APPLICATION_CREDENTIALS,
    TELEGRAM_TOKEN,
    ADMIN_CHAT_ID,
)
from logger import setup_logging


logger = logging.getLogger(__name__)


async def create_intent(
    project_id, display_name, training_phrases_parts, message_texts
):

    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)

    training_phrases = []

    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message],
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    return True


async def train_from_json(phrases_path, project_id):
    """Обучает DialogFlow из JSON файла."""
    try:
        with open(phrases_path, "r", encoding="UTF-8") as file:
            intents_data = json.load(file)

        created_count = 0
        failed_count = 0

        for display_name, data in intents_data.items():
            questions = data["questions"]
            answer = data["answer"]

            success = await create_intent(
                project_id=project_id,
                display_name=display_name,
                training_phrases_parts=questions,
                message_texts=[answer],
            )

            if success:
                created_count += 1
            else:
                failed_count += 1

        return created_count, failed_count

    except FileNotFoundError:
        raise FileNotFoundError(f"Файл не найден: {PHRASES_PATH}")
    except KeyError as e:
        raise KeyError(f"Ошибка в структуре JSON: отсутствует ключ {e}")
    except Exception as e:
        raise Exception(f"Произошла ошибка при обучении: {e}")


def list_intents(project_id):
    """Выводит список существующих интентов."""
    try:
        intents_client = dialogflow.IntentsClient()
        parent = dialogflow.AgentsClient.agent_path(project_id)

        intents = intents_client.list_intents(request={"parent": parent})

        intents_list = []

        for intent in intents:
            intents_list.append(
                {
                    "name": intent.display_name,
                    "id": intent.name,
                    "training_phrases_count": len(intent.training_phrases),
                }
            )

        return intents_list

    except Exception as e:
        raise Exception(f"Ошибка при получении списка интентов: {e}")


async def main():

    setup_logging(
        telegram_token=TELEGRAM_TOKEN,
        admin_chat_id=ADMIN_CHAT_ID,
        logger_instance=None,
    )

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    logger.info("Скрипт train_dialogflow запущен")

    print("Текущие интенты в DialogFlow:")
    print("=" * 50)

    try:
        intents = list_intents(project_id=PROJECT_ID)
        for intent in intents:
            print(f"Имя: {intent['name']}")
            print(f"ID: {intent['id']}")
            print(f"Количество тренировочных фраз: {intent['training_phrases_count']}")
            print("-" * 30)

        print(f"Всего интентов: {len(intents)}")
        print("=" * 50)

    except Exception as e:
        print(f"Ошибка при получении списка интентов: {e}")
        return

    print("\nНачинаю обучение DialogFlow...")

    try:
        created_count, failed_count = await train_from_json(
            phrases_path=PHRASES_PATH, project_id=PROJECT_ID
        )

        print("\n" + "=" * 50)
        print(f"Обучение DialogFlow завершено!")
        print(f"Создано интентов: {created_count}")
        print(f"Ошибок: {failed_count}")
        print("=" * 50)

    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
    except KeyError as e:
        print(f"Ошибка в JSON файле: {e}")
    except Exception as e:
        print(f"Ошибка при обучении: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nСкрипт остановлен пользователем (Ctrl+C)")
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        raise
