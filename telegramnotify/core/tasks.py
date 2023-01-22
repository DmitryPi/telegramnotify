import asyncio

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from config import celery_app
from telegramnotify.tgbots.bots import SenderBot
from telegramnotify.utils.orm import get_users_exclude_expired

from .services import user_wallet_decrement_by_pay_rate

User = get_user_model()
sender_bot = SenderBot()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def users_update_premium_expired_task(self):
    """
    Loop through users
    Skip users with premium_status=permanent
    Check if premium_expire date passed
        set premium_status=expired
    TODO: make it dumb
    """
    with transaction.atomic():
        try:
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
        except Exception as exc:
            raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def users_update_wallet_decrement_by_pay_rate_task(self):
    """Dumb task: to loop over users and call user_wallet_decrement_by_pay_rate()"""
    with transaction.atomic():
        try:
            users = get_users_exclude_expired()
            for user in users:
                user_wallet_decrement_by_pay_rate(user)
        except Exception as exc:
            raise self.retry(exc=exc)
