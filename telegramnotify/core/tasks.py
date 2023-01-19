import asyncio

from django.contrib.auth import get_user_model
from django.utils import timezone

from config import celery_app
from telegramnotify.tgbots.bots import SenderBot
from telegramnotify.utils.orm import (
    get_parser_entries,
    get_users_exclude_expired,
    update_parser_entries_sent,
)

User = get_user_model()
sender_bot = SenderBot()


@celery_app.task()
def users_update_premium_expired_task():
    """
    Loop through users
    Skip users with premium_status=permanent
    Check if premium_expire date passed
        set premium_status=expired
    """
    users = get_users_exclude_expired()
    for user in users:
        if user.premium_status == User.PremiumStatus.permanent:
            continue
        if timezone.now() > user.premium_expire:
            user.premium_status = User.PremiumStatus.expired
            user.save(update_fields=["premium_status"])
            asyncio.run(
                sender_bot.raw_send_message(
                    user.tg_id, sender_bot.premium_expired_message
                )
            )


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
