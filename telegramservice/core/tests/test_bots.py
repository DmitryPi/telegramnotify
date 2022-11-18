import re
from collections import namedtuple

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.test import TestCase
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from telegramservice.users.tests.factories import UserFactory

from ..bots import SenderBot, TelegramBot
from ..models import ParserEntry
from ..utils import datetime_days_ahead
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
        self.settings = [
            "Добавить сервис",
            "Удалить сервис",
            "Добавить слова",
            "Удалить слово",
        ]

    def test_init(self):
        yesno = ["Да", "Нет"]
        commands = {
            "start": "/start",
            "help": "/help",
            "pay": "/pay",
            "account": "/account",
            "settings": "/settings",
            "techsupport": "/support",
            "cancel": "/cancel",
        }
        assert len(self.telegram_bot.services) == 1
        assert isinstance(self.telegram_bot.services, list)
        assert self.telegram_bot.settings == self.settings
        assert self.telegram_bot.yesno == yesno
        assert self.telegram_bot.commands == commands

    def test_auth_invalid_msg(self):
        msg = f"🔴 Пройдите регистрацию.\n\nИспользуйте команду - {self.telegram_bot.commands['start']}"
        assert self.telegram_bot.auth_invalid_msg == msg

    def test_error_msg(self):
        msg = "🔴 Ой, что-то пошло не так.\n\nПрограммист оповещен об этом!"
        assert self.telegram_bot.error_msg == msg

    def test_build_keyboard(self):
        btns = [100, 200, 300, 400, 500]
        keyboard = self.telegram_bot.build_keyboard(btns)
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert isinstance(keyboard["keyboard"], list)
        assert isinstance(keyboard["keyboard"][0], list)
        assert isinstance(keyboard["keyboard"][0][0], KeyboardButton)
        assert keyboard["keyboard"][0][0]["text"] == 100
        assert keyboard["keyboard"][0][4]["text"] == 500

    def test_build_inline_keyboard(self):
        """Test inline keyboard of 5 items"""
        settings = self.settings
        settings.append("test")
        # instance
        keyboard = self.telegram_bot.build_inline_keyboard(settings)
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert isinstance(keyboard["inline_keyboard"][0][0], InlineKeyboardButton)
        # grid 1
        keyboard = self.telegram_bot.build_inline_keyboard(settings, grid=1)
        assert len(keyboard["inline_keyboard"]) == 5
        # grid 2
        keyboard = self.telegram_bot.build_inline_keyboard(settings, grid=2)
        assert len(keyboard["inline_keyboard"]) == 3
        # grid 3
        keyboard = self.telegram_bot.build_inline_keyboard(settings, grid=3)
        assert len(keyboard["inline_keyboard"]) == 2

    @async_to_sync
    async def test_auth_complete(self):
        # Emulate telegram update object
        Update = namedtuple("Update", ["effective_user"])
        UserTG = namedtuple("UserTG", ["id", "username", "first_name"])
        user = UserTG(333, "Test", "Test")
        # Emulate telegram context object
        Context = namedtuple("Context", ["user_data"])
        user_data = {"words": ["test", "апи", "bot"], "service": "FL.ru"}
        # init update & context
        update = Update(user)
        context = Context(user_data)
        # delete user:
        await self.telegram_bot.auth_complete(update, context)
        user = await User.objects.prefetch_related("services").aget(username="Test")
        assert user.tg_id == 333
        assert user.username == "Test"
        assert user.bill == 0
        assert user.wallet == 0
        assert user.words == user_data["words"]
        assert user.premium_status == User.PremiumStatus.trial
        assert user.premium_expire.day == datetime_days_ahead(3).day
        # services
        services = user.services.all()
        assert len(services) == 1
        assert services[0].title == user_data["service"]
