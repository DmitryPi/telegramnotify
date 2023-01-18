import json
import uuid

from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from telegramnotify.core.models import Ticket


@receiver(post_save, sender=Ticket)
def post_save_create_ticket_send_reply_msg_task(sender, instance, **kwargs):
    """
    Проверка если ticket reply и status=UNSOLVED
        - Сигнал создает celery-задачу ticket_send_reply_msg_task

    Полная процедура описана в моделе Ticket
    """

    if instance.reply and instance.status == instance.Status.UNSOLVED:
        salt = uuid.uuid4().hex[:6]
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1, period=IntervalSchedule.SECONDS
        )
        PeriodicTask.objects.create(
            name=f"Send reply to tg [{instance.user}] : salt{salt}",
            task="telegramnotify.core.tasks.ticket_send_reply_msg_task",
            interval=schedule,
            enabled=True,
            one_off=True,
            args=json.dumps([instance.pk]),
        )
