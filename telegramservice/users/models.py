from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


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

    # fields
    tg_id = models.IntegerField(_("Telegram ID"), unique=True, null=True, blank=True)
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    # service fields
    services = ArrayField(models.CharField(max_length=55), blank=True, default=list)
    words = ArrayField(models.CharField(max_length=112), blank=True, default=list)
    # business logic fields
    bill = models.DecimalField(_("Тариф"), max_digits=11, decimal_places=2, default=0)
    wallet = models.DecimalField(
        _("Баланс"), max_digits=11, decimal_places=2, default=0
    )
    premium_status = models.CharField(
        _("Premium Status"),
        max_length=55,
        choices=PremiumStatus.choices,
        default=PremiumStatus.expired,
    )
    premium_expire = models.DateTimeField(blank=True, default="")

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
