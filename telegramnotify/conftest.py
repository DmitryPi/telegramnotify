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
def user_trial(db) -> User:
    return UserFactory(premium_status=User.PremiumStatus.trial)


@pytest.fixture
def user_regular(db) -> User:
    return UserFactory(premium_status=User.PremiumStatus.regular)


@pytest.fixture
def user_permanent(db) -> User:
    return UserFactory(premium_status=User.PremiumStatus.permanent)


@pytest.fixture
def user_expired(db) -> User:
    return UserFactory(premium_status=User.PremiumStatus.expired)


@pytest.fixture
def parser_entry(db) -> ParserEntry:
    return ParserEntryFactory()
