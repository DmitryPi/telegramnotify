import asyncio

from config import celery_app
from telegramnotify.tgbots.bots import SenderBot
from telegramnotify.utils.orm import (
    get_parser_entries,
    get_users_exclude_expired,
    save_parser_entry,
    update_parser_entries_sent,
)

from .bots import FLParser

sender_bot = SenderBot()


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

    users = get_users_exclude_expired()

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
