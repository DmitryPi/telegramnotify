# import re
# from collections import namedtuple

from django.test import TestCase

from ..bots import SenderBot
from .factories import ParserEntryFactory


class TestSenderBot(TestCase):
    def setUp(self):
        self.sender_bot = SenderBot()

    def test_build_message(self):
        parser_entry = ParserEntryFactory()
        message = self.sender_bot.build_message(parser_entry)
        assert parser_entry.title in message
        assert parser_entry.description in message
        assert parser_entry.budget in message
        assert parser_entry.deadline in message
        assert parser_entry.url in message

    def test_search_words(self):
        pass
        # User = namedtuple("User", ["words"])
        # Entry = namedtuple("Entry", ["title", "description", "words"])
        # tests = [
        #     Entry("Something nice", "else", ["бот", "test", "nice"]),
        #     Entry("Something бот", "else bot", ["bot", "test", "nice"]),
        #     Entry("Something тест", "else bot", ["bot", "тест", "nice"]),
        # ]
        # test_incorrect = [
        #     Entry("Something nice", "else", ["omething", "test", "бот"]),
        #     Entry("Something бот", "else bot", ["апи", "se", "thi"]),
        #     Entry("Something тест", "else bot", ["что", "test", "meth"]),
        # ]
        # for entry in tests:
        #     result = self.sender_bot.search_words(entry)
        #     assert isinstance(result, re.Match)
        # for entry in test_incorrect:
        #     result = self.sender_bot.search_words(entry)
        #     assert not result
