from django.utils import timezone


def datetime_days_ahead(days: int) -> timezone:
    now = timezone.now()
    delta = timezone.timedelta(days=days)
    return now + delta
