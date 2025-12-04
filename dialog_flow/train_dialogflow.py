import os
import sys
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

    print(f"Создан интент: {display_name}")
    return True


async def train_from_json():
    """Обучает DialogFlow из JSON файла."""
    try:
        with open(PHRASES_PATH, "r", encoding="UTF-8") as file:
            intents_data = json.load(file)

        for display_name, data in intents_data.items():
            questions = data["questions"]
            answer = data["answer"]

            print(f"Создаю интент: {display_name}")
            await create_intent(
                project_id=PROJECT_ID,
                display_name=display_name,
                training_phrases_parts=questions,
                message_texts=[answer],
            )
            print(f"Интент '{display_name}' успешно создан\n")

        print("Обучение DialogFlow завершено!")

    except FileNotFoundError:
        print("Ошибка: файл phrases.json не найден")
    except KeyError as e:
        print(f"Ошибка в структуре JSON: отсутствует ключ {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def list_intents():
    """Выводит список существующих интентов."""
    try:
        intents_client = dialogflow.IntentsClient()
        parent = dialogflow.AgentsClient.agent_path(PROJECT_ID)

        intents = intents_client.list_intents(request={"parent": parent})

        print("Существующие интенты:")
        print("=" * 50)
        for intent in intents:
            print(f"Имя: {intent.display_name}")
            print(f"ID: {intent.name}")
            print(f"Количество тренировочных фраз: {len(intent.training_phrases)}")
            print("-" * 30)
    except Exception as e:
        print(f"Ошибка при получении списка интентов: {e}")


if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    print("Текущие интенты в DialogFlow:")
    list_intents()
    print("\n" + "=" * 50 + "\n")

    response = input(
        "Хотите обучить DialogFlow новым интентам из phrases.json? (y/n): "
    )

    if response.lower() == "y":
        print("\nНачинаю обучение DialogFlow...")
        asyncio.run(train_from_json())
    else:
        print("Обучение отменено.")
