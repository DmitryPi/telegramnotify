from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = [
        "uuid",
        "telegram_payment_charge_id",
        "provider_payment_charge_id",
    ]
    fieldsets = (
        (None, {"fields": ("uuid", "user", "status", "currency", "total_amount")}),
        (
            _("Телеграм"),
            {
                "fields": (
                    "invoice_payload",
                    "telegram_payment_charge_id",
                    "provider_payment_charge_id",
                )
            },
        ),
    )

    list_display = ["uuid", "status", "total_amount", "currency"]
