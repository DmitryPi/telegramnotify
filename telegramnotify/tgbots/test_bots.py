import re
from collections import namedtuple
from typing import TypeAlias

from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth import get_user_model
from django.test import TestCase
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from telegramnotify.core.models import Order
from telegramnotify.core.tests.factories import ServiceFactory
from telegramnotify.parsers.models import ParserEntry
from telegramnotify.parsers.tests.factories import ParserEntryFactory
from telegramnotify.tickets.models import Ticket
from telegramnotify.tickets.tests.factories import TicketFactory
from telegramnotify.users.tests.factories import UserFactory
from telegramnotify.utils.other import datetime_days_ahead

from .bots import SenderBot, TelegramBot

User = get_user_model()
Update: TypeAlias = namedtuple
Context: TypeAlias = namedtuple


def emulate_update_object(
    tg_id=333,
    username="Test",
    first_name="Test Name",
    text="test text",
    order_total_amount=10000,
) -> Update:
    """Эмуляция объекта Update для телеграм бота

    Examples:
        Update.effective_user.id
        Update.message.text
        Update.message.successful_payment

    Args:
        tg_id (int, optional): Telegram user id defaults to 333.
        username (str, optional): Default to 'Test'
        first_name (str, optional): Default to 'Test Name'
        text (str, optional): Default to 'test text'

    Returns:
        Update: namedtuple with fields: id, username, first_name
    """
    Update = namedtuple("Update", ["effective_user", "message"])
    order = {
        "total_amount": order_total_amount,
        "currency": "RUB",
        "invoice_payload": "payload",
        "telegram_payment_charge_id": "test_id",
        "provider_payment_charge_id": "test_id",
    }
    User = namedtuple("UserTG", ["id", "username", "first_name"])
    user = User(id=tg_id, username=username, first_name=first_name)
    Message = namedtuple("Message", ["text", "successful_payment"])
    message = Message(text=text, successful_payment=order)
    return Update(user, message)


def emulate_context_object(context_dict: dict = {}) -> Context:
    """Эмуляция объекта Context для телеграм бота

    Args:
        context_dict (dict): Telegram user_context_data

    Returns:
        Context: namedtuple with fields user_data
    """
    Context = namedtuple("Context", ["user_data"])
    return Context(context_dict)


class TestSenderBot(TestCase):
    def setUp(self):
        self.sender_bot = SenderBot()
        self.entries = [
            ParserEntry(title="Something nice", description="else"),
            ParserEntry(title="Something БОТ", description="test pfs"),
            ParserEntry(title="Something-test-", description="terific pfs"),
        ]

    def test_build_reply_message(self):
        ticket = TicketFactory(reply="test")
        message = self.sender_bot.build_reply_message(ticket)
        assert message == "@admin: test"

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
        # init update & context
        context_data = {"words": ["test", "апи", "bot"], "service": "FL.ru"}
        update = await sync_to_async(emulate_update_object)()
        context = await sync_to_async(emulate_context_object)(context_data)
        # create user
        await self.telegram_bot.auth_complete(update, context)
        # load user
        user = await User.objects.prefetch_related("services").aget(username="Test")
        # test created user data
        assert user.tg_id == 333
        assert user.username == "Test"
        assert user.pay_rate == 0
        assert user.wallet == 0
        assert user.words == context_data["words"]
        assert user.premium_status == User.PremiumStatus.trial
        assert user.premium_expire.day == datetime_days_ahead(3).day
        # test user services
        services = user.services.all()
        assert len(services) == 1
        assert services[0].title == context_data["service"]

    @async_to_sync
    async def test_techsupport_msg(self):
        """Test Ticket creation"""
        # init update & context
        context_data = {"words": ["test", "апи", "bot"], "service": "FL.ru"}
        update = await sync_to_async(emulate_update_object)()
        context = await sync_to_async(emulate_context_object)(context_data)
        # create user
        await self.telegram_bot.auth_complete(update, context)
        # load user
        user = await User.objects.aget(username="Test")
        # run techsupport_msg
        try:
            await self.telegram_bot.techsupport_msg(update, context)
        except AttributeError:  # handle update.message.reply_text line
            pass
        finally:
            ticket = await Ticket.objects.prefetch_related("user").afirst()
            assert ticket.user.tg_id == user.tg_id
            assert ticket.message == "test text"
            assert not ticket.reply

    @async_to_sync
    async def test_successful_payment_callback(self):
        # init update & context
        user = await sync_to_async(UserFactory)(tg_id=333)
        order = await Order.objects.afirst()
        update = await sync_to_async(emulate_update_object)(tg_id=user.tg_id)
        context = await sync_to_async(emulate_context_object)()
        # test order
        assert not order
        # run successful_payment_callback
        try:
            await self.telegram_bot.successful_payment_callback(update, context)
        except AttributeError:  # handle update.message.reply_text line
            pass
        finally:
            user = await User.objects.aget(tg_id=user.tg_id)
            order = await Order.objects.prefetch_related("user").afirst()
            # test user data
            assert user.wallet == 100
            # test order data
            assert order.user == user
            assert order.status == Order.Status.SUCCESS
            assert order.invoice_payload == "payload"
            assert order.currency == "RUB"
            assert order.total_amount == 100
            assert order.telegram_payment_charge_id == "test_id"
            assert order.provider_payment_charge_id == "test_id"
