from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from telegramservice.core.models import Service


class User(AbstractUser):
    """
    Default custom user model for TelegramService.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # choices
    class PremiumStatus(models.TextChoices):
        trial = "trial", _("Trial")
        regular = "regular", _("Regular")
        permanent = "permanent", _("Permanent")
        expired = "expired", _("Expired")

    # relations
    services = models.ManyToManyField(Service, blank=True)
    # fields
    tg_id = models.BigIntegerField(
        _("Telegram ID"), db_index=True, unique=True, null=True, blank=True
    )
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    words = ArrayField(models.CharField(max_length=112), blank=True, default=list)
    # business logic fields
    bill = models.DecimalField(_("Тариф"), max_digits=11, decimal_places=2, default=0)
    wallet = models.DecimalField(
        _("Баланс"), max_digits=11, decimal_places=2, default=0
    )
    premium_status = models.CharField(
        _("Статус"),
        max_length=55,
        choices=PremiumStatus.choices,
        default=PremiumStatus.expired,
    )
    premium_expire = models.DateTimeField(_("Действует до"), null=True, blank=True)
    # misc
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    def __str__(self):
        return f"{self.tg_id} : {self.username}"

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def update_wallet(self, amount: int):
        """Update wallet value"""
        self.wallet += Decimal(amount)
        self.save()
