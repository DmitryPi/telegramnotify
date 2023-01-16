import pytest
from celery.result import EagerResult
from django.contrib.auth import get_user_model
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from telegramnotify.users.tests.factories import UserFactory

from ..models import ParserEntry, Ticket
from ..tasks import (
    clean_oneoff_tasks,
    parse_flru_task,
    sender_bot_task,
    ticket_send_reply_msg_task,
    users_update_premium_expired_task,
)
from .factories import ParserEntryFactory, ServiceFactory, TicketFactory

User = get_user_model()


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


@pytest.mark.django_db
def test_ticket_send_reply_msg_task(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    ticket = TicketFactory(reply="test", status=Ticket.Status.UNSOLVED)
    ticket_send_reply_msg_task(ticket.id)
    ticket = Ticket.objects.get(id=ticket.id)
    assert ticket.status == Ticket.Status.SOLVED


@pytest.mark.django_db
def test_users_update_premium_expired_task(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    UserFactory.create_batch(
        10, premium_expire=timezone.now() - timezone.timedelta(hours=1)
    )
    result = users_update_premium_expired_task.delay()
    users = User.objects.all()
    assert isinstance(result, EagerResult)
    for user in users:
        if user.premium_status == User.PremiumStatus.permanent:
            assert user.premium_status == User.PremiumStatus.permanent
        else:
            assert user.premium_status == User.PremiumStatus.expired


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
