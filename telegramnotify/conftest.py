import pytest

from telegramnotify.parsers.models import ParserEntry
from telegramnotify.parsers.tests.factories import ParserEntryFactory
from telegramnotify.users.models import User
from telegramnotify.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def parser_entry(db) -> ParserEntry:
    return ParserEntryFactory()
