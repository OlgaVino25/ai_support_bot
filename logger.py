import logging
import traceback
import requests
from settings import TELEGRAM_TOKEN, ADMIN_CHAT_ID


logger = logging.getLogger("app_logger")


class TelegramErrorsHandler(logging.Handler):

    def emit(self, record):
        if record.levelno < logging.WARNING:
            return

        if not TELEGRAM_TOKEN or not ADMIN_CHAT_ID:
            return

        try:
            msg = f"Ошибка в боте\n\n"
            msg += f"Время: {record.asctime}\n"
            msg += f"Уровень: {record.levelname}\n"
            msg += f"Модуль: {record.module}\n"
            msg += f"Сообщение: {record.getMessage()}\n"

            if record.exc_info:
                exc_type, exc_value, exc_tb = record.exc_info
                tb_text = "".join(
                    traceback.format_exception(exc_type, exc_value, exc_tb)
                )

                if len(tb_text) > 1000:
                    tb_text = tb_text[-1000:]
                msg += f"\nТрейсбек:\n{tb_text}"

            self._send_to_telegram(msg)

        except Exception as e:
            print(f"Не удалось отправить лог в Telegram: {e}")

    def _send_to_telegram(self, msg):
        """Синхронная отправка сообщения через Telegram Bot API"""
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        payload = {"chat_id": ADMIN_CHAT_ID, "text": msg}
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                print(f"⚠️ Не удалось отправить сообщение в Telegram: {response.text}")
        except Exception as e:
            print(f"❌ Не удалось отправить сообщение в Telegram: {e}")


def setup_logging(logger_instance=None):
    """Настраивает логирование.

    Args:
        logger_instance: Логгер для настройки. Если None, настраивается корневой логгер.
    """
    if logger_instance is None:
        logger_instance = logging.getLogger()

    logger_instance.setLevel(logging.DEBUG)
    logger_instance.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(process)d - %(levelname)s - %(pathname)s - %(lineno)d - %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    if TELEGRAM_TOKEN and ADMIN_CHAT_ID:
        telegram_handler = TelegramErrorsHandler()
        telegram_handler.setLevel(logging.WARNING)
        logger.addHandler(telegram_handler)

    return logger_instance
