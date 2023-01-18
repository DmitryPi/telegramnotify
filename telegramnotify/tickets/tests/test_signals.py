import json

import pytest
from django_celery_beat.models import PeriodicTask

from telegramnotify.core.models import Ticket
from telegramnotify.core.tests.factories import TicketFactory


@pytest.mark.django_db
def test_post_save_create_ticket_send_reply_msg_task():
    ticket = TicketFactory(reply="", status=Ticket.Status.UNSOLVED)
    tasks_qs = PeriodicTask.objects.all()
    assert not len(tasks_qs)
    # ticket update
    ticket.reply = "test reply"
    ticket.save()
    tasks_qs = PeriodicTask.objects.all()
    task = tasks_qs[0]
    assert len(tasks_qs) == 1
    assert task.task == "telegramnotify.tickets.tasks.ticket_send_reply_msg_task"
    assert task.enabled
    assert task.one_off
    assert json.loads(task.args)[0] == ticket.id


@pytest.mark.django_db
def test_post_save_create_ticket_send_reply_msg_task_if_solved_and_reply():
    ticket = TicketFactory(reply="test", status=Ticket.Status.SOLVED)
    tasks_qs = PeriodicTask.objects.all()
    assert not len(tasks_qs)
    # ticket update
    ticket.reply = "test reply"
    ticket.save()
    tasks_qs = PeriodicTask.objects.all()
    assert not len(tasks_qs)


@pytest.mark.django_db
def test_post_save_create_ticket_send_reply_msg_task_if_unsolved_and_reply():
    ticket = TicketFactory(reply="test", status=Ticket.Status.UNSOLVED)
    tasks_qs = PeriodicTask.objects.all()
    assert len(tasks_qs) == 1
    # ticket update
    ticket.reply = "test reply"
    ticket.save()
    tasks_qs = PeriodicTask.objects.all()
    assert len(tasks_qs) == 2
    for task in tasks_qs:
        print(task)
        assert task.task == "telegramnotify.tickets.tasks.ticket_send_reply_msg_task"
        assert task.enabled
        assert task.one_off
