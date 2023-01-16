import asyncio

from django_celery_beat.models import PeriodicTask

from config import celery_app

from .bots import SenderBot
from .parsers import FLParser
from .utils import (
    get_parser_entries,
    get_users,
    save_parser_entry,
    update_parser_entries_sent,
    users_update_premium_expired,
)


@celery_app.task(ignore_result=True)
def clean_oneoff_tasks():
    """Clean oneoff tasks with enabled=False"""
    PeriodicTask.objects.filter(one_off=True, enabled=False).delete()


@celery_app.task(bind=True)
def ticket_send_reply_msg_task(self):
    """
    TODO: this
    """
    pass


@celery_app.task()
def users_update_premium_expired_task():
    users_update_premium_expired()


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
    get entries with sent=False
    get users
    Loop through users and entries
    If theres match on user words
    => send message to telegram user

    TODO: test build_entry_message-build_message incorrect func name
    TODO: async search_words / send message
    """
    entries = get_parser_entries()

    if not entries:  # save 1 request to db
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
