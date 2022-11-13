import environ

from telegramservice.core.bots import TelegramBot


def run():
    env = environ.Env()
    env.read_env(".env")
    telegram_bot = TelegramBot(env)
    telegram_bot.run()
