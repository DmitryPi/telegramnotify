import pytest

from telegramservice.core.models import ParserEntry
from telegramservice.core.tests.factories import ParserEntryFactory
from telegramservice.users.models import User
from telegramservice.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def parser_entry(db) -> ParserEntry:
    return ParserEntryFactory()
