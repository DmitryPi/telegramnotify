import uuid as uuid_lib

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Order(TimeStampedModel):
    """User buy order"""

    # choices
    class Status(models.TextChoices):
        FAILURE = "FAILURE", _("Failure")
        PENDING = "PENDING", _("Pending")
        SUCCESS = "SUCCESS", _("Success")

    # relations
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # fields
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    status = models.CharField(
        max_length=55, choices=Status.choices, default=Status.PENDING
    )
    invoice_payload = models.CharField(max_length=55)
    currency = models.CharField(max_length=5)
    total_amount = models.DecimalField(max_digits=11, decimal_places=2)
    telegram_payment_charge_id = models.CharField(max_length=100, editable=False)
    provider_payment_charge_id = models.CharField(max_length=100, editable=False)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"{self.status} : {self.uuid}"


class Service(TimeStampedModel):
    """Service websites to parse"""

    # fields
    title = models.CharField(_("Title"), max_length=55)
    url_body = models.URLField(_("URL body"), max_length=100)
    url_query = models.URLField(_("URL query"), max_length=100, blank=True)
    daily_price = models.DecimalField(
        _("Daily Price"), max_digits=5, decimal_places=2, default=0
    )

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

    def __str__(self):
        return f"{self.title} : {self.daily_price}"
