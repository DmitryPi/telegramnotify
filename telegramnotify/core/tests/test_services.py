from decimal import Decimal

from django.contrib.auth import get_user_model

from ..services import user_wallet_decrement_by_pay_rate
from .factories import build_services

User = get_user_model()


def test_user_wallet_decrement_by_pay_rate(user):
    user_old = user
    services, total_price = build_services()
    for s in services:
        user.services.add(s)
    # update
    user_wallet_decrement_by_pay_rate(user)
    user = User.objects.get(pk=user.id)
    # tests
    assert isinstance(total_price, Decimal)
    assert isinstance(user.pay_rate, Decimal)
    assert user.pay_rate == total_price
    assert user.wallet < user_old.wallet
    assert user.wallet == Decimal(user_old.wallet - total_price)
