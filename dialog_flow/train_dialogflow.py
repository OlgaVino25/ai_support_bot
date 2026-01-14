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
)
from logger import setup_logging


logger = logging.getLogger(__name__)


async def create_intent(
    project_id, display_name, training_phrases_parts, message_texts
):
    try:
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

        logger.info(f"Создан интент: {display_name}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании интента {display_name}: {e}")
        raise


async def train_from_json():
    """Обучает DialogFlow из JSON файла."""
    try:
        with open(PHRASES_PATH, "r", encoding="UTF-8") as file:
            intents_data = json.load(file)

        logger.info(f"Начинаю обучение DialogFlow из файла: {PHRASES_PATH}")

        for display_name, data in intents_data.items():
            questions = data["questions"]
            answer = data["answer"]

            logger.info(f"Создаю интент: {display_name}")
            await create_intent(
                project_id=PROJECT_ID,
                display_name=display_name,
                training_phrases_parts=questions,
                message_texts=[answer],
            )
            logger.info(f"Интент '{display_name}' успешно создан\n")

        logger.info("Обучение DialogFlow завершено!")

    except FileNotFoundError:
        logger.error(f"Файл не найден: {PHRASES_PATH}")
        raise
    except KeyError as e:
        logger.error(f"Ошибка в структуре JSON: отсутствует ключ {e}")
        raise
    except Exception as e:
        logger.error(f"Произошла ошибка при обучении: {e}")
        raise


def list_intents():
    """Выводит список существующих интентов."""
    try:
        intents_client = dialogflow.IntentsClient()
        parent = dialogflow.AgentsClient.agent_path(PROJECT_ID)

        intents = intents_client.list_intents(request={"parent": parent})

        logger.info("Существующие интенты:")
        logger.info("=" * 50)

        intent_count = 0
        for intent in intents:
            logger.info(f"Имя: {intent.display_name}")
            logger.info(f"ID: {intent.name}")
            logger.info(
                f"Количество тренировочных фраз: {len(intent.training_phrases)}"
            )
            logger.info("-" * 30)
            intent_count += 1

        logger.info(f"Всего интентов: {intent_count}")
        return intent_count
    except Exception as e:
        logger.error(f"Ошибка при получении списка интентов: {e}")
        raise


async def main():

    setup_logging()

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    logger.info("Скрипт train_dialogflow запущен")

    logger.info("Текущие интенты в DialogFlow:")
    list_intents()
    logger.info("=" * 50)

    response = input(
        "Хотите обучить DialogFlow новым интентам из phrases.json? (y/n): "
    )

    logger.info(f"Пользовательский выбор: {response}")

    if response.lower() == "y":
        logger.info("Начинаю обучение DialogFlow...")
        await train_from_json()
    else:
        logger.info("Обучение отменено пользователем.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Скрипт остановлен пользователем (Ctrl+C)")
    except Exception as e:
        logger.exception("Непредвиденная ошибка при выполнении скрипта")
        raise
