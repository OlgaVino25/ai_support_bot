from pathlib import Path
from environs import Env


env = Env()
env.read_env()

# Базовые пути
BASE_DIR = Path(__file__).parent
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
PHRASES_PATH = BASE_DIR / "dialog_flow" / "phrases.json"

# DialogFlow
PROJECT_ID = env.str("PROJECT_ID")
GOOGLE_APPLICATION_CREDENTIALS = str(CREDENTIALS_PATH)

# Telegram
TELEGRAM_TOKEN = env.str("CONTEXT_ASSISTANT_BOT_TG_TOKEN")
ADMIN_CHAT_ID = env.str("ADMIN_CHAT_ID")

# VK
VK_TOKEN = env.str("VK_GROUP_TOKEN")
