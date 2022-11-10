from datetime import datetime, timedelta


def datetime_days_ahead(days: int) -> datetime:
    now = datetime.now()
    delta = timedelta(days=days)
    return now + delta
