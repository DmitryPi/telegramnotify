from django.apps import AppConfig


class TicketsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "telegramnotify.tickets"

    def ready(self):
        try:
            import telegramnotify.tickets.signals  # noqa
        except ImportError:
            pass
