import os

import django
import environ

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from telegramservice.bots.bot import TelegramBot  # noqa E402

if __name__ == "__main__":
    env = environ.Env()
    env.read_env(".env")
    telegram_bot = TelegramBot(env)
    telegram_bot.run()
