from datetime import datetime, timedelta

from ..utils import datetime_days_ahead


def test_datetime_days_ahead(self):
    examples = [
        (datetime_days_ahead(0), datetime.now() + timedelta(days=0)),
        (datetime_days_ahead(3), datetime.now() + timedelta(days=3)),
        (datetime_days_ahead(10), datetime.now() + timedelta(days=10)),
    ]
    for dt, res in examples:
        assert isinstance(dt, datetime)
        assert dt == res
