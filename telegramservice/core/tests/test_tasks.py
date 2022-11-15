import pytest
from celery.result import EagerResult
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from ..models import ParserEntry
from ..tasks import clean_oneoff_tasks, parse_flru_task, sender_bot_task
from .factories import ParserEntryFactory, TargetFactory


@pytest.mark.django_db
def test_clean_oneoff_tasks(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=10,
        period=IntervalSchedule.SECONDS,
    )
    for i in range(5):
        PeriodicTask.objects.create(
            interval=schedule,
            name=f"task {i}",
            task=f"test task {i}",
            one_off=True,
            enabled=False,
        )
    one_off_tasks = PeriodicTask.objects.filter(one_off=True)
    assert len(one_off_tasks) == 5
    # execute task
    result = clean_oneoff_tasks.delay()
    one_off_tasks = PeriodicTask.objects.filter(one_off=True)
    assert isinstance(result, EagerResult)
    assert not len(one_off_tasks)


@pytest.mark.slow
@pytest.mark.django_db
def test_parse_flru_task(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    target = TargetFactory()
    entries = ParserEntry.objects.all()
    assert target.title == "FL.ru"
    assert not len(entries)
    # execute task
    result = parse_flru_task.delay()
    entries = ParserEntry.objects.all()
    assert isinstance(result, EagerResult)
    assert len(entries) > 10


@pytest.mark.django_db
def test_sender_bot_task(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    ParserEntryFactory.create_batch(10)
    entries = ParserEntry.objects.all()
    assert len(entries) == 10
    for entry in entries:
        assert not entry.sent
    # execute task
    result = sender_bot_task.delay()
    entries = ParserEntry.objects.all()
    assert isinstance(result, EagerResult)
    for entry in entries:
        assert entry.sent
