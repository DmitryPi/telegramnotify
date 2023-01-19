import pytest
from celery.result import EagerResult

from telegramnotify.parsers.models import ParserEntry
from telegramnotify.parsers.tests.factories import ParserEntryFactory
from telegramnotify.users.tests.factories import UserFactory

from ..tasks import sender_bot_task


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
