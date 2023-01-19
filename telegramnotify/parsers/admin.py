from django.contrib import admin

from .models import ParserEntry


def update_sent_true(modeladmin, request, qs):
    qs.update(sent=True)


def update_sent_false(modeladmin, request, qs):
    qs.update(sent=False)


@admin.register(ParserEntry)
class ParserEntryAdmin(admin.ModelAdmin):
    actions = [update_sent_true, update_sent_false]

    list_display = ["pid", "short_title", "source", "sent", "created"]
