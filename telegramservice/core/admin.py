from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Order, ParserEntry, Ticket, Target


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

    list_display = ["uuid", "status", "total_amount", "currency", "created"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["user", "short_message", "status", "created"]


@admin.register(ParserEntry)
class ParserEntryAdmin(admin.ModelAdmin):
    list_display = ["short_title", "source", "sent", "created"]


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ["title", "url_body", "created"]
