from collections import namedtuple

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from telegramnotify.users.tests.factories import UserFactory

from ..models import ParserEntry
from ..utils import (
    get_parser_entries,
    get_parser_entry,
    get_users,
    get_users_all,
    save_parser_entry,
    update_parser_entries_sent,
    user_set_status_permanent,
)
from .factories import ParserEntryFactory

User = get_user_model()


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

    def test_update_parser_entries_sent(self):
        ParserEntryFactory.create_batch(10)
        entries = get_parser_entries()
        assert len(entries) == 10
        # update
        update_parser_entries_sent(entries)
        entries = get_parser_entries()
        assert not len(entries)

    def test_get_users_all(self):
        UserFactory.create_batch(10)
        users = get_users_all()
        assert len(users) == 10

    def test_get_users(self):
        UserFactory.create_batch(10)
        users = get_users()
        for user in users:
            assert user.premium_status != User.PremiumStatus.expired

    def test_user_set_status_permanent(self):
        permanent_date = timezone.now() + timezone.timedelta(days=3650)
        UserFactory.create_batch(10)
        users = get_users_all()
        [user_set_status_permanent(user) for user in users]
        users = get_users()
        assert len(users) == 10
        for user in users:
            assert user.premium_status == User.PremiumStatus.permanent
            assert permanent_date.year == user.premium_expire.year
