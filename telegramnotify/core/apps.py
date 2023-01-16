from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "telegramnotify.core"

    def ready(self):
        try:
            import telegramnotify.core.signals  # noqa
        except ImportError:
            pass
