from decimal import Decimal

from django.test import TestCase

from telegramservice.users.models import User

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
        user.update_wallet(3)
        user = User.objects.get(pk=user.id)
        assert user.wallet == 314
        assert isinstance(user.wallet, Decimal)
