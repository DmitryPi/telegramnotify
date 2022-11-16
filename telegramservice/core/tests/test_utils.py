from collections import namedtuple

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from factory.fuzzy import FuzzyChoice

from telegramservice.users.tests.factories import UserFactory

from ..models import ParserEntry
from ..utils import (
    datetime_days_ahead,
    get_parser_entries,
    get_parser_entry,
    get_users,
    save_parser_entry,
    search_word,
    update_parser_entries_sent,
    users_update_premium_expired,
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

    def test_datetime_days_ahead(self):
        """TODO: refactor"""
        examples = [
            (datetime_days_ahead(0), timezone.now() + timezone.timedelta(days=0)),
            (datetime_days_ahead(3), timezone.now() + timezone.timedelta(days=3)),
            (datetime_days_ahead(10), timezone.now() + timezone.timedelta(days=10)),
        ]
        for dt, res in examples:
            pass

    def test_search_word(self):
        Test = namedtuple("Test", ["text", "correct", "incorrect"])
        tests = [
            Test("Тест telegramстрока", "тест", "telegram"),
            Test("Тест bot telegramстрока", "BOT", "telegram"),
            Test("Тест.bot.telegramстрока", "boT", "telegram"),
            Test("Тест-бот-telegramстрока", "Бот", "telegram"),
        ]

        for test in tests:
            assert search_word(test.text, test.correct)
            assert not search_word(test.text, test.incorrect)

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

    def test_get_users(self):
        UserFactory.create_batch(20)
        users = get_users()
        for user in users:
            assert user.premium_status != User.PremiumStatus.expired

    def test_users_update_premium_expired(self):
        """Test update for premium_status of trial and regular"""
        hour_before = timezone.now() - timezone.timedelta(hours=1)
        hour_ahead = timezone.now() + timezone.timedelta(hours=1)
        # hour before
        UserFactory.create_batch(
            20,
            premium_status=FuzzyChoice(
                [User.PremiumStatus.trial, User.PremiumStatus.regular]
            ),
            premium_expire=hour_before,
        )
        # hour ahead
        UserFactory.create_batch(
            10,
            premium_status=FuzzyChoice(
                [User.PremiumStatus.trial, User.PremiumStatus.regular]
            ),
            premium_expire=hour_ahead,
        )
        users = get_users()
        assert len(users) == 30
        users_update_premium_expired()
        users = get_users()
        assert len(users) == 10
        for user in users:
            assert timezone.now() < user.premium_expire

    def test_users_update_premium_expired_permament(self):
        """
        Test if permanent users are exluded from evaluation
        Even if for some reason permanent_status date passed,
        Permanent status won't be changed
        """
        hour_before = timezone.now() - timezone.timedelta(hours=1)
        UserFactory.create_batch(
            10,
            premium_status=User.PremiumStatus.permanent,
            premium_expire=hour_before,
        )
        users = get_users()
        assert len(users) == 10
        users_update_premium_expired()
        users = get_users()
        assert len(users) == 10
        for user in users:
            assert user.premium_status == User.PremiumStatus.permanent
            assert timezone.now() > user.premium_expire
