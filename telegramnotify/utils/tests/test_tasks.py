import pytest
from celery.result import EagerResult
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from ..tasks import clean_oneoff_tasks


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
