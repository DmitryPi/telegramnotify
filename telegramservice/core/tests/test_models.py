import re

from django.test import TestCase

from ..models import Order, ParserEntry
from .factories import OrderFactory, ParserEntryFactory


class TestOrder(TestCase):
    def setUp(self):
        self.batch_size = 10
        self.objects = OrderFactory.create_batch(size=self.batch_size)

    def test_create(self):
        assert len(self.objects) == self.batch_size

    def test_delete(self):
        for obj in self.objects:
            obj.delete()
        qs = Order.objects.all()
        assert not len(qs)

    def test_fields(self):
        for obj in self.objects:
            assert obj.user.id
            assert obj.uuid
            assert obj.status == Order.Status.SUCCESS
            assert obj.currency == "RUB"
            assert obj.total_amount >= 0
            assert obj.telegram_payment_charge_id
            assert obj.provider_payment_charge_id


class TestParserEntry(TestCase):
    def setUp(self):
        self.batch_size = 10
        self.objects = ParserEntryFactory.create_batch(size=self.batch_size)

    def test_create(self):
        assert len(self.objects) == self.batch_size

    def test_update(self):
        new_title = "new title"
        for obj in self.objects:
            obj.title = new_title
            obj.save()
        for obj in self.objects:
            assert obj.title == new_title

    def test_delete(self):
        for obj in self.objects:
            obj.delete()
        qs = ParserEntry.objects.all()
        assert not len(qs)

    def test_fields(self):
        for obj in self.objects:
            assert re.match(r"^(.*)-(\d+)$", obj.pid)  # match Fl.ru-123
            assert len(obj.title) > 10
            assert len(obj.description) > 10
            assert obj.budget
            assert obj.deadline
            assert obj.url
            assert obj.source == "FL.ru"
            assert isinstance(obj.sent, bool)
