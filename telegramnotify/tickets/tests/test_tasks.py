import pytest
from celery.result import EagerResult

from ..models import Ticket
from ..tasks import ticket_send_reply_msg_task
from .factories import TicketFactory


@pytest.mark.django_db
def test_ticket_send_reply_msg_task(settings):
    """Эмуляция отправки Ticket.reply сообщения в телеграм."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    ticket = TicketFactory(reply="test", status=Ticket.Status.UNSOLVED)
    result = ticket_send_reply_msg_task.delay(ticket.id)
    ticket = Ticket.objects.get(id=ticket.id)
    assert isinstance(result, EagerResult)
    assert ticket.status == Ticket.Status.SOLVED
