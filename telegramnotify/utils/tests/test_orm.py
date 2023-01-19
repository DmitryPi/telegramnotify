from collections import namedtuple

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from telegramnotify.parsers.models import ParserEntry
from telegramnotify.parsers.tests.factories import ParserEntryFactory
from telegramnotify.users.tests.factories import UserFactory

from ..orm import (
    get_parser_entries,
    get_parser_entry,
    get_users_all,
    get_users_exclude_expired,
    save_parser_entry,
    update_parser_entries_sent,
    user_set_status_permanent,
)

User = get_user_model()
Data = namedtuple(
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
project_data = Data(
    pid="FL.ru-123",
    url="https://www.fl.ru/projects/5073180/dodelat-sayt-php-na-wordpress.html",
    title="Доделать сайт php на wordpress",
    description="Доделать сайт php на wordpress",
    budget="ожидает предложений",
    deadline="по договоренности",
    source="FL.ru",
    sent=False,
)


@pytest.mark.django_db
def test_save_parser_entry():
    entries = ParserEntry.objects.all()
    assert not len(entries)
    for i in range(3):
        save_parser_entry(project_data)
        entries = ParserEntry.objects.all()
        assert len(entries) == 1


@pytest.mark.django_db
def test_get_parser_entry():
    # assert if not exist
    res = get_parser_entry("FL.ru-123")
    assert not res
    # assert if exists
    save_parser_entry(project_data)
    res = get_parser_entry("FL.ru-123")
    assert res.pid


@pytest.mark.django_db
def test_get_parser_entries():
    ParserEntryFactory.create_batch(10)
    entries = get_parser_entries()
    assert len(entries) == 10


@pytest.mark.django_db
def test_update_parser_entries_sent():
    ParserEntryFactory.create_batch(10)
    entries = get_parser_entries()
    assert len(entries) == 10
    # update
    update_parser_entries_sent(entries)
    entries = get_parser_entries()
    assert not len(entries)


@pytest.mark.django_db
def test_get_users_all():
    UserFactory.create_batch(10)
    users = get_users_all()
    assert len(users) == 10


@pytest.mark.django_db
def test_get_users():
    UserFactory.create_batch(10)
    users = get_users_exclude_expired()
    for user in users:
        assert user.premium_status != User.PremiumStatus.expired


@pytest.mark.django_db
def test_user_set_status_permanent():
    permanent_date = timezone.now() + timezone.timedelta(days=3650)
    UserFactory.create_batch(10)
    users = get_users_all()
    [user_set_status_permanent(user) for user in users]
    users = get_users_exclude_expired()
    assert len(users) == 10
    for user in users:
        assert user.premium_status == User.PremiumStatus.permanent
        assert permanent_date.year == user.premium_expire.year
