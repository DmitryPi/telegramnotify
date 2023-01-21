from decimal import Decimal

from django.contrib.auth import get_user_model

from ..services import user_wallet_decrement_by_pay_rate
from .factories import build_services

User = get_user_model()


def test_user_wallet_decrement_by_pay_rate(user_regular):
    user_old = user_regular
    services, total_price = build_services()
    for s in services:
        user_regular.services.add(s)
    # update
    user_wallet_decrement_by_pay_rate(user_regular)
    user_regular = User.objects.get(pk=user_regular.id)
    # tests
    assert isinstance(total_price, Decimal)
    assert isinstance(user_regular.pay_rate, Decimal)
    assert user_regular.pay_rate == total_price
    assert user_regular.wallet < user_old.wallet
    assert user_regular.wallet == Decimal(user_old.wallet - total_price)
