import random
import uuid as uuid_lib

from factory import Faker, LazyAttribute, SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal

from telegramnotify.users.tests.factories import UserFactory

from ..models import Order, ParserEntry, Service, Ticket


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


class ParserEntryFactory(DjangoModelFactory):
    pid = LazyAttribute(lambda a: f"{a.source}-{random.randrange(1, 555)}")
    title = Faker("sentence", nb_words=3, locale="ru_RU")
    description = Faker("text")
    budget = LazyAttribute(lambda a: f"{random.randrange(500, 5555)} рублей")
    deadline = "по договоренности"
    url = "https://www.fl.ru/projects/5073180/dodelat-sayt-php-na-wordpress.html"
    source = FuzzyChoice(choices=["FL.ru"])
    sent = False

    class Meta:
        model = ParserEntry


class ServiceFactory(DjangoModelFactory):
    title = FuzzyChoice(choices=["FL.ru"])
    url_body = "https://www.fl.ru/"
    url_query = "https://www.fl.ru/projects/"
    daily_price = FuzzyDecimal(1, 5)

    class Meta:
        model = Service


class TicketFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    message = Faker("text", locale="ru_RU")
    status = FuzzyChoice(
        choices=[
            Ticket.Status.SOLVED,
            Ticket.Status.UNSOLVED,
        ]
    )

    class Meta:
        model = Ticket
