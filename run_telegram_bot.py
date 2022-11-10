import environ

from telegramparserservice.bots.bot import TelegramBot

if __name__ == "__main__":
    env = environ.Env()
    env.read_env(".env")
    telegram_bot = TelegramBot(env)
    telegram_bot.run()
