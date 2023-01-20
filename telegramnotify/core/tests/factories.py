import uuid as uuid_lib
from decimal import Decimal
from random import randint, uniform

from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal

from telegramnotify.users.tests.factories import UserFactory

from ..models import Order, Service


class OrderFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    status = FuzzyChoice(
        choices=[
            Order.Status.FAILURE,
            Order.Status.PENDING,
            Order.Status.SUCCESS,
        ]
    )
    invoice_payload = "Payload"
    currency = "RUB"
    total_amount = FuzzyDecimal(100, 5000)
    telegram_payment_charge_id = str(uuid_lib.uuid4())
    provider_payment_charge_id = str(uuid_lib.uuid4())

    class Meta:
        model = Order


class ServiceFactory(DjangoModelFactory):
    title = FuzzyChoice(choices=["FL.ru"])
    url_body = "https://www.fl.ru/"
    url_query = "https://www.fl.ru/projects/"
    daily_price = FuzzyDecimal(1, 5)

    class Meta:
        model = Service


def build_services() -> tuple[tuple[Service], Decimal]:
    service_prices = [
        Decimal(str(round(uniform(1, 5), 1))) for _ in range(randint(1, 5))
    ]
    total_price = sum(service_prices)
    services = (ServiceFactory(daily_price=i) for i in service_prices)
    return (services, total_price)
