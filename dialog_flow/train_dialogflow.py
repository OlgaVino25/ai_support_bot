import os
import sys
import logging
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import json
import asyncio
from google.cloud import dialogflow
from google.api_core.exceptions import InvalidArgument, AlreadyExists

from settings import (
    PHRASES_PATH,
    PROJECT_ID,
    GOOGLE_APPLICATION_CREDENTIALS,
)
from logger import setup_logging

logger = logging.getLogger(__name__)


def get_intent_by_display_name(intents_client, parent, display_name):
    """Находит интент по display_name."""
    try:
        intents = intents_client.list_intents(request={"parent": parent})
        for intent in intents:
            if intent.display_name == display_name:
                return intent
        return None
    except Exception as e:
        logger.error(f"Ошибка при поиске интента '{display_name}': {e}")
        return None


async def create_intent(
    project_id, display_name, training_phrases_parts, message_texts
):
    """Создает новый интент."""
    try:
        intents_client = dialogflow.IntentsClient()
        parent = dialogflow.AgentsClient.agent_path(project_id)

        existing_intent = get_intent_by_display_name(
            intents_client, parent, display_name
        )

        if existing_intent:
            logger.warning(
                f"Интент '{display_name}' уже существует (ID: {existing_intent.name}). "
                f"Используйте update_intent для обновления."
            )
            return False

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

    except AlreadyExists:
        logger.error(f"Интент '{display_name}' уже существует.")
        return False
    except InvalidArgument as e:
        logger.error(f"Ошибка в аргументах для интента '{display_name}': {e}")
        return False
    except Exception as e:
        logger.error(f"Неизвестная ошибка при создании интента '{display_name}': {e}")
        return False


async def update_intent(
    project_id, display_name, training_phrases_parts, message_texts
):
    """Обновляет существующий интент."""
    try:
        intents_client = dialogflow.IntentsClient()
        parent = dialogflow.AgentsClient.agent_path(project_id)

        existing_intent = get_intent_by_display_name(
            intents_client, parent, display_name
        )

        if not existing_intent:
            logger.warning(f"Интент '{display_name}' не найден для обновления.")
            return False

        training_phrases = []
        for training_phrases_part in training_phrases_parts:
            part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
            training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
            training_phrases.append(training_phrase)

        text = dialogflow.Intent.Message.Text(text=message_texts)
        message = dialogflow.Intent.Message(text=text)

        existing_intent.training_phrases = training_phrases
        existing_intent.messages = [message]

        response = intents_client.update_intent(request={"intent": existing_intent})

        logger.info(f"Обновлен интент: {display_name}")
        return True

    except Exception as e:
        logger.error(f"Ошибка при обновлении интента '{display_name}': {e}")
        return False


async def delete_intent(project_id, display_name):
    """Удаляет существующий интент."""
    try:
        intents_client = dialogflow.IntentsClient()
        parent = dialogflow.AgentsClient.agent_path(project_id)

        existing_intent = get_intent_by_display_name(
            intents_client, parent, display_name
        )

        if not existing_intent:
            logger.warning(f"Интент '{display_name}' не найден для удаления.")
            return False

        intents_client.delete_intent(name=existing_intent.name)
        logger.info(f"Удален интент: {display_name}")
        return True

    except Exception as e:
        logger.error(f"Ошибка при удалении интента '{display_name}': {e}")
        return False


async def train_from_json(mode="create"):
    """Обучает DialogFlow из JSON файла."""
    try:
        with open(PHRASES_PATH, "r", encoding="UTF-8") as file:
            intents_data = json.load(file)

        logger.info(f"Начинаю обучение DialogFlow из файла: {PHRASES_PATH}")
        logger.info(f"Режим работы: {mode}")

        created_count = 0
        updated_count = 0
        failed_count = 0

        for display_name, data in intents_data.items():
            questions = data["questions"]
            answer = data["answer"]

            logger.info(f"Обработка интента: {display_name}")

            if mode == "create":
                success = await create_intent(
                    project_id=PROJECT_ID,
                    display_name=display_name,
                    training_phrases_parts=questions,
                    message_texts=[answer],
                )
                if success:
                    created_count += 1
                else:
                    failed_count += 1

            elif mode == "update":
                success = await update_intent(
                    project_id=PROJECT_ID,
                    display_name=display_name,
                    training_phrases_parts=questions,
                    message_texts=[answer],
                )
                if success:
                    updated_count += 1
                else:
                    failed_count += 1

            elif mode == "delete":
                success = await delete_intent(
                    project_id=PROJECT_ID,
                    display_name=display_name,
                )
                if success:
                    logger.info(f"Интент '{display_name}' удален")
                else:
                    failed_count += 1

        if mode == "create":
            logger.info(
                f"Обучение завершено! Создано: {created_count}, Ошибок: {failed_count}"
            )
        elif mode == "update":
            logger.info(
                f"Обновление завершено! Обновлено: {updated_count}, Ошибок: {failed_count}"
            )
        elif mode == "delete":
            logger.info(f"Удаление завершено! Ошибок: {failed_count}")

        return created_count, updated_count, failed_count

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

        logger.info("Текущие интенты в DialogFlow:")
        logger.info("=" * 50)

        intent_count = 0
        custom_intents = []

        for intent in intents:
            if not intent.display_name.startswith("Default"):
                custom_intents.append(intent.display_name)
                logger.info(f"Имя: {intent.display_name}")
                logger.info(f"ID: {intent.name}")
                logger.info(
                    f"Количество тренировочных фраз: {len(intent.training_phrases)}"
                )
                logger.info("-" * 30)
                intent_count += 1

        logger.info(f"Всего пользовательских интентов: {intent_count}")
        return custom_intents

    except Exception as e:
        logger.error(f"Ошибка при получении списка интентов: {e}")
        raise


async def main():
    """Основная асинхронная функция."""
    setup_logging()

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    logger.info("Скрипт train_dialogflow запущен")

    custom_intents = list_intents()
    logger.info("=" * 50)

    with open(PHRASES_PATH, "r", encoding="UTF-8") as file:
        intents_data = json.load(file)

    existing_from_file = [
        name for name in intents_data.keys() if name in custom_intents
    ]

    if existing_from_file:
        logger.warning(
            f"Следующие интенты уже существуют в DialogFlow: {', '.join(existing_from_file)}"
        )

    print("\n" + "=" * 50)
    print("Выберите действие:")
    print("1. Создать новые интенты (пропустить существующие)")
    print("2. Обновить существующие интенты")
    print("3. Удалить все интенты из phrases.json")
    print("4. Показать текущие интенты и выйти")
    print("=" * 50)

    choice = input("Ваш выбор (1-4): ").strip()

    if choice == "1":
        logger.info("Режим: создание новых интентов")
        created, updated, failed = await train_from_json(mode="create")
        print(f"\nРезультат: создано {created}, ошибок {failed}")

    elif choice == "2":
        logger.info("Режим: обновление существующих интентов")
        created, updated, failed = await train_from_json(mode="update")
        print(f"\nРезультат: обновлено {updated}, ошибок {failed}")

    elif choice == "3":
        confirm = input("Вы уверены, что хотите удалить эти интенты? (y/n): ").lower()
        if confirm == "y":
            logger.info("Режим: удаление интентов")
            created, updated, failed = await train_from_json(mode="delete")
            print(f"\nУдаление завершено, ошибок: {failed}")
        else:
            logger.info("Удаление отменено")

    elif choice == "4":
        print("\nТекущие интенты:")
        for intent in custom_intents:
            print(f"  - {intent}")
    else:
        logger.warning("Неверный выбор. Выход.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Скрипт остановлен пользователем (Ctrl+C)")
    except Exception as e:
        logger.exception("Непредвиденная ошибка при выполнении скрипта")
        raise
