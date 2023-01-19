import pytest
from celery.result import EagerResult
from django.contrib.auth import get_user_model

from telegramnotify.core.tests.factories import ServiceFactory
from telegramnotify.users.tests.factories import UserFactory

from ..models import ParserEntry
from ..tasks import parse_flru_task, sender_bot_task
from .factories import ParserEntryFactory

User = get_user_model()


@pytest.mark.slow
@pytest.mark.django_db
def test_parse_flru_task(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    service = ServiceFactory()
    entries = ParserEntry.objects.all()
    assert service.title == "FL.ru"
    assert not len(entries)
    # execute task
    result = parse_flru_task.delay()
    entries = ParserEntry.objects.all()
    assert isinstance(result, EagerResult)
    assert len(entries) > 10


@pytest.mark.django_db
def test_sender_bot_task(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    # create test objects
    words = ["bot", "test", "python"]
    UserFactory(words=words)
    for word in words:
        ParserEntryFactory(title={word.capitalize()})
    ParserEntryFactory.create_batch(7)
    # run pre-tests
    entries = ParserEntry.objects.all()
    assert len(entries) == 10
    for entry in entries:
        assert not entry.sent
    # execute task
    result = sender_bot_task.delay()
    # run tests
    entries = ParserEntry.objects.all()
    assert isinstance(result, EagerResult)
    for entry in entries:
        assert entry.sent
