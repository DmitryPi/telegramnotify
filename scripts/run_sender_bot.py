import environ

from telegramservice.core.bots import SenderBot


def run():
    env = environ.Env()
    env.read_env(".env")
    telegram_bot = SenderBot(env)
    telegram_bot.run()
