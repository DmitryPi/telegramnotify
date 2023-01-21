from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


def update_premium_expired() -> None:
    pass


def user_wallet_decrement_by_pay_rate(user: User) -> None:
    """
    1. Обновить актуальное значение сметы: User.update_pay_rate
    2. Получить обновленного юзера
    3. Произвести декремент кошелька, значением user.pay_rate

    TODO: more tests
    """
    with transaction.atomic():
        if user.premium_status == User.PremiumStatus.permanent:
            return None
        user.update_pay_rate()
        user = User.objects.get(pk=user.id)
        user.update_wallet(-user.pay_rate)
