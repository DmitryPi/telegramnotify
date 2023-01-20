from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Ticket(TimeStampedModel):
    """
    Тикет технической поддержки
    TODO: Добавить поддержку диалога.
    """

    # choices
    class Status(models.TextChoices):
        SOLVED = "SOLVED", _("Solved")
        UNSOLVED = "UNSOLVED", _("Unsolved")

    # relations
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # fields
    message = models.TextField(_("Вопрос"))
    reply = models.TextField(_("Ответ"), blank=True)
    status = models.CharField(
        max_length=55, choices=Status.choices, default=Status.UNSOLVED
    )

    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")

    def __str__(self):
        return f"{self.user} : {self.status}"

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    @property
    def short_message(self, len=40):
        return self.message[:len]

    @property
    def short_reply(self, len=40):
        return self.reply[:len]
