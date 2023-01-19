import uuid as uuid_lib

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
