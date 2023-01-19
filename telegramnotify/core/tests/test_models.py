from decimal import Decimal

from django.test import TestCase

from ..models import Order, Service
from .factories import OrderFactory, ServiceFactory


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
            assert isinstance(obj.status, Order.Status)
            assert obj.currency == "RUB"
            assert obj.total_amount >= 0
            assert obj.telegram_payment_charge_id
            assert obj.provider_payment_charge_id


class TestService(TestCase):
    def setUp(self):
        self.batch_size = 10
        self.objects = ServiceFactory.create_batch(size=self.batch_size)

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
        qs = Service.objects.all()
        assert not len(qs)

    def test_fields(self):
        for obj in self.objects:
            assert obj.title == "FL.ru"
            assert "https" in obj.url_body
            assert "https" in obj.url_query
            assert isinstance(obj.daily_price, Decimal)
