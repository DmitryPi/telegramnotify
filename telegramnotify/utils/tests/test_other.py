from collections import namedtuple

from django.utils import timezone

from ..other import datetime_days_ahead, list_into_chunks, search_word


def test_list_into_chunks():
    tests = [
        ([1], [[1]]),
        ([1, 2], [[1, 2]]),
        ([1, 2, 3], [[1, 2], [3]]),
        ([1, 2, 3, 4], [[1, 2], [3, 4]]),
    ]
    for test, res in tests:
        result = list_into_chunks(test, n=2)
        assert isinstance(result, list)
        assert isinstance(result[0], list)
        assert result == res


def test_datetime_days_ahead():
    tests = [
        (datetime_days_ahead(0), timezone.now() + timezone.timedelta(days=0)),
        (datetime_days_ahead(3), timezone.now() + timezone.timedelta(days=3)),
        (datetime_days_ahead(10), timezone.now() + timezone.timedelta(days=10)),
    ]
    for test, res in tests:
        assert test.day == res.day
        assert test.month == res.month
        assert test.year == res.year


def test_search_word():
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
