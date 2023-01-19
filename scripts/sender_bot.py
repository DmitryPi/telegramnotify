from telegramnotify.tgbots.bots import SenderBot


def run():
    telegram_bot = SenderBot()
    telegram_bot.run()
