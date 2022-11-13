from django.test import TestCase

from ..models import Order
from .factories import OrderFactory


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
