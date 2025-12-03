import os

from environs import Env

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType

import vk_handlers as vk_h


if __name__ == "__main__":
    env = Env()
    env.read_env()

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env.str(
        "GOOGLE_APPLICATION_CREDENTIALS", "credentials.json"
    )

    vk_token = env.str("VK_GROUP_TOKEN")
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    print("Бот запущен. Для обучения DialogFlow запустите отдельно train_dialogflow.py")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            vk_h.echo(event, vk_api)
