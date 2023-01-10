from decimal import Decimal

from django.test import TestCase

from telegramnotify.core.tests.factories import ServiceFactory
from telegramnotify.users.models import User

from .factories import UserFactory


class TestUser(TestCase):
    def setUp(self):
        pass

    def test_get_absolute_url(self):
        user = UserFactory()
        assert user.get_absolute_url() == f"/users/{user.username}/"

    def test_update_wallet(self):
        user = UserFactory()
        assert user.wallet == 0
        # update wallet
        user.update_wallet(100)
        user = User.objects.get(pk=user.id)
        assert user.wallet == 100
        assert isinstance(user.wallet, Decimal)
        # update wallet
        user.update_wallet(55.5)
        user.update_wallet(155.5)
        user.update_wallet(3.5)
        user = User.objects.get(pk=user.id)
        assert user.wallet == 314.5
        assert isinstance(user.wallet, Decimal)

    def test_update_bill(self):
        user = UserFactory()
        services = [
            ServiceFactory(daily_price=3),
            ServiceFactory(daily_price=1.5),
            ServiceFactory(daily_price=2),
        ]
        # add services
        [user.services.add(s) for s in services]
        user = User.objects.get(pk=user.id)
        assert user.bill == 0
        assert len(user.services.all()) == 3
        # update bill
        user.update_bill()
        user = User.objects.get(pk=user.id)
        assert user.bill == 6.5
        assert isinstance(user.bill, Decimal)
