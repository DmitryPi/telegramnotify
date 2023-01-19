import asyncio

from config import celery_app
from telegramnotify.core.bots import SenderBot

from .models import Ticket


@celery_app.task(bind=True)
def ticket_send_reply_msg_task(self, ticket_id: int):
    sender_bot = SenderBot()
    ticket = Ticket.objects.get(id=ticket_id)
    message = sender_bot.build_reply_message(ticket)
    asyncio.run(sender_bot.raw_send_message(ticket.user.tg_id, message))
    ticket.status = Ticket.Status.SOLVED
    ticket.save()
