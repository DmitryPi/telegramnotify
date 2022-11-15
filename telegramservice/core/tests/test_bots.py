import re

from django.test import TestCase

from telegramservice.users.tests.factories import UserFactory

from ..bots import SenderBot
from ..models import ParserEntry
from .factories import ParserEntryFactory


class TestSenderBot(TestCase):
    def setUp(self):
        self.sender_bot = SenderBot()
        self.entries = [
            ParserEntry(title="Something nice", description="else"),
            ParserEntry(title="Something БОТ", description="test pfs"),
            ParserEntry(title="Something-test-", description="terific pfs"),
        ]

    def test_build_message(self):
        parser_entry = ParserEntryFactory()
        message = self.sender_bot.build_message(parser_entry)
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
