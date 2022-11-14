from collections import namedtuple

from django.test import TestCase
from django.utils import timezone

from telegramservice.users.tests.factories import UserFactory

from ..models import ParserEntry
from ..utils import (
    datetime_days_ahead,
    get_parser_entries,
    get_parser_entry,
    get_users,
    save_parser_entry,
)
from .factories import ParserEntryFactory


class TestUtils(TestCase):
    def setUp(self):
        self.Data = namedtuple(
            "Data",
            [
                "pid",
                "url",
                "title",
                "description",
                "budget",
                "deadline",
                "source",
                "sent",
            ],
        )
        self.project_data = self.Data(
            pid="FL.ru-123",
            url="https://www.fl.ru/projects/5073180/dodelat-sayt-php-na-wordpress.html",
            title="Доделать сайт php на wordpress",
            description="Доделать сайт php на wordpress",
            budget="ожидает предложений",
            deadline="по договоренности",
            source="FL.ru",
            sent=False,
        )

    def test_datetime_days_ahead(self):
        """TODO: refactor"""
        examples = [
            (datetime_days_ahead(0), timezone.now() + timezone.timedelta(days=0)),
            (datetime_days_ahead(3), timezone.now() + timezone.timedelta(days=3)),
            (datetime_days_ahead(10), timezone.now() + timezone.timedelta(days=10)),
        ]
        for dt, res in examples:
            pass

    def test_save_parser_entry(self):
        entries = ParserEntry.objects.all()
        assert not len(entries)
        for i in range(3):
            save_parser_entry(self.project_data)
            entries = ParserEntry.objects.all()
            assert len(entries) == 1

    def test_get_parser_entry(self):
        # assert if not exist
        res = get_parser_entry("FL.ru-123")
        assert not res
        # assert if exists
        save_parser_entry(self.project_data)
        res = get_parser_entry("FL.ru-123")
        assert res.pid

    def test_get_parser_entries(self):
        ParserEntryFactory.create_batch(10)
        entries = get_parser_entries()
        assert len(entries) == 10

    def test_get_users(self):
        UserFactory.create_batch(10)
        users = get_users()
        assert len(users) == 10
