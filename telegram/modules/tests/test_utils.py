from datetime import datetime, timedelta
from unittest import TestCase

from ..utils import datetime_days_ahead, load_config


class TestUtils(TestCase):
    def setUp(self):
        pass

    def test_load_config(self):
        sections = ["MAIN", "TELEGRAM", "SENTRY"]
        config = load_config()
        self.assertTrue(config)
        config_sections = config.sections()
        for section in sections:
            self.assertTrue(section in config_sections)

    def test_datetime_days_ahead(self):
        examples = [
            (datetime_days_ahead(0), datetime.now() + timedelta(days=0)),
            (datetime_days_ahead(3), datetime.now() + timedelta(days=3)),
            (datetime_days_ahead(10), datetime.now() + timedelta(days=10)),
        ]
        for dt, res in examples:
            assert isinstance(dt, datetime)
            assert dt == res
