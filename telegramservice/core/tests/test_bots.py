import environ
from django.test import TestCase

from ..bots import SenderBot
from .factories import ParserEntryFactory


class TestSenderBot(TestCase):
    def setUp(self):
        env = environ.Env()
        env.read_env(".env")
        self.sender_bot = SenderBot(env)

    def test_build_message(self):
        parser_entry = ParserEntryFactory()
        message = self.sender_bot.build_message(parser_entry)
        assert parser_entry.title in message
        assert parser_entry.description in message
        assert parser_entry.budget in message
        assert parser_entry.deadline in message
        assert parser_entry.url in message
