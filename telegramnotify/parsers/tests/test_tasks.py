import pytest
from celery.result import EagerResult
from django.contrib.auth import get_user_model

from telegramnotify.core.tests.factories import ServiceFactory

from ..models import ParserEntry
from ..tasks import parse_flru_task

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
