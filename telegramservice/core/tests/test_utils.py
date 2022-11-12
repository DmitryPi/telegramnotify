from datetime import datetime

from django.utils import timezone

from ..utils import datetime_days_ahead


def test_datetime_days_ahead():
    examples = [
        (datetime_days_ahead(0), timezone.now() + timezone.timedelta(days=0)),
        (datetime_days_ahead(3), timezone.now() + timezone.timedelta(days=3)),
        (datetime_days_ahead(10), timezone.now() + timezone.timedelta(days=10)),
    ]
    for dt, res in examples:
        assert isinstance(dt, datetime)
        assert dt == res
