import asyncio

from django.contrib.auth import get_user_model
from django.utils import timezone
from django_celery_beat.models import PeriodicTask

from config import celery_app

from .bots import SenderBot
from .models import Ticket
from .parsers import FLParser
from .utils import (
    get_parser_entries,
    get_users,
    save_parser_entry,
    update_parser_entries_sent,
)

User = get_user_model()


@celery_app.task(ignore_result=True)
def clean_oneoff_tasks():
    """Clean oneoff tasks with enabled=False"""
    PeriodicTask.objects.filter(one_off=True, enabled=False).delete()


@celery_app.task(bind=True)
def ticket_send_reply_msg_task(self, ticket_id: int):
    sender_bot = SenderBot()
    ticket = Ticket.objects.get(id=ticket_id)
    message = sender_bot.build_reply_message(ticket)
    asyncio.run(sender_bot.raw_send_message(ticket.user.tg_id, message))
    ticket.status = Ticket.Status.SOLVED
    ticket.save()


@celery_app.task()
def users_update_premium_expired_task():
    """
    Loop through users
    Skip users with premium_status=permanent
    Check if premium_expire date passed
        set premium_status=expired
    """
    users = get_users()
    for user in users:
        if user.premium_status == User.PremiumStatus.permanent:
            continue
        if timezone.now() > user.premium_expire:
            user.premium_status = User.PremiumStatus.expired
            user.save(update_fields=["premium_status"])


@celery_app.task(bind=True)
def parse_flru_task(self):
    """
    Init parser
    Parse fl.ru projects from /projects page
    Visit each project
    save parser entry
    """
    parser = FLParser()
    projects_info = parser.get_projects_info()
    for i, info in enumerate(projects_info):
        # update task progress
        self.update_state(
            state="PROGRESS", meta={"current": i, "total": len(projects_info)}
        )
        # get data => save data
        project_data = parser.get_project_data(info)
        save_parser_entry(project_data)


@celery_app.task(bind=True)
def sender_bot_task(self):
    """
    Description:
        get ParserEntry with sent=False
        get Users
        Loop through Users and ParserEntry
            If theres match on user words
                send message to telegram user
        update ParserEntry to sent=True

    TODO: async search_words / send message
    """
    entries = get_parser_entries()

    if not entries:
        return None

    users = get_users()
    sender_bot = SenderBot()

    for i, user in enumerate(users):
        # update task progress
        self.update_state(state="PROGRESS", meta={"current": i, "total": len(users)})
        # search user words on particular entry
        for entry in entries:
            match = sender_bot.search_words(user, entry)
            if not match:
                continue
            # if there's match
            message = sender_bot.build_entry_message(entry)
            asyncio.run(sender_bot.raw_send_message(user.tg_id, message))
    # update entries set sent=True
    update_parser_entries_sent(entries)
