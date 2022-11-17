import re

from django.contrib.auth import get_user_model
from django.test import TestCase

from telegramservice.users.tests.factories import UserFactory

from ..bots import SenderBot, TelegramBot
from ..models import ParserEntry
from .factories import ParserEntryFactory, ServiceFactory

User = get_user_model()


class TestSenderBot(TestCase):
    def setUp(self):
        self.sender_bot = SenderBot()
        self.entries = [
            ParserEntry(title="Something nice", description="else"),
            ParserEntry(title="Something БОТ", description="test pfs"),
            ParserEntry(title="Something-test-", description="terific pfs"),
        ]

    def test_build_entry_message(self):
        parser_entry = ParserEntryFactory()
        message = self.sender_bot.build_entry_message(parser_entry)
        self.assertIn(parser_entry.title, message)
        self.assertIn(parser_entry.description, message)
        self.assertIn(parser_entry.budget, message)
        self.assertIn(parser_entry.deadline, message)
        self.assertIn(parser_entry.url, message)

    def test_search_words(self):
        user = UserFactory(words=["бот", "test", "nice"])
        for entry in self.entries:
            result = self.sender_bot.search_words(user, entry)
            self.assertTrue(isinstance(result, re.Match))

    def test_search_words_incorrect(self):
        user = UserFactory(words=["дизайн", "1с", "telegram"])
        for entry in self.entries:
            result = self.sender_bot.search_words(user, entry)
            self.assertFalse(result)

    def test_run(self):
        ParserEntryFactory.create_batch(10)
        self.sender_bot.run()
        entries = ParserEntry.objects.all()
        for entry in entries:
            self.assertTrue(entry.sent)


class TestTelegramBot(TestCase):
    def setUp(self):
        ServiceFactory()
        self.telegram_bot = TelegramBot()

    def test_init(self):
        settings = [
            "Добавить сервис",
            "Добавить слова",
            "Удалить сервис",
            "Удалить слово",
        ]
        yesno = ["Да", "Нет"]
        commands = {
            "start": "/start",
            "help": "/help",
            "pay": "/pay",
            "balance": "/balance",
            "bill": "/bill",
            "settings": "/settings",
            "techsupport": "/support",
            "cancel": "/cancel",
        }
        assert len(self.telegram_bot.services) == 1
        assert isinstance(self.telegram_bot.services, list)
        assert self.telegram_bot.settings == settings
        assert self.telegram_bot.yesno == yesno
        assert self.telegram_bot.commands == commands

    def test_auth_invalid_msg(self):
        msg = f"Пройдите регистрацию.\nИспользуйте команду - {self.telegram_bot.commands['start']}"
        assert self.telegram_bot.auth_invalid_msg == msg

    def test_error_msg(self):
        msg = "Ой, что-то пошло не так.\nПрограммист оповещен об этом!"
        assert self.telegram_bot.error_msg == msg

    # @pytest.mark.db_async
    # def test_auth_complete(self):
    #     # Emulate telegram update object
    #     Update = namedtuple("Update", ["effective_user"])
    #     UserTG = namedtuple("UserTG", ["id", "username", "first_name"])
    #     user = UserTG(333, "Test2", "Test")
    #     # Emulate telegram context object
    #     Context = namedtuple("Context", ["user_data"])
    #     user_data = {"words": ["test", "апи", "bot"], "service": "FL.ru"}
    #     # init update & context
    #     update = Update(user)
    #     context = Context(user_data)
    #     # delete user:
    #     asyncio.run(self.telegram_bot.auth_complete(update, context))
