import random
import uuid as uuid_lib

from factory import Faker, LazyAttribute, SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

from telegramservice.users.tests.factories import UserFactory

from ..models import Order, ParserEntry, Target, Ticket


class OrderFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    status = Order.Status.SUCCESS
    invoice_payload = "Payload"
    currency = "RUB"
    total_amount = Faker("random_number")
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
    sent = FuzzyChoice(choices=[False, True])

    class Meta:
        model = ParserEntry


class TargetFactory(DjangoModelFactory):
    title = FuzzyChoice(choices=["FL.ru"])
    url_body = "https://www.fl.ru/"
    url_query = "https://www.fl.ru/projects/"

    class Meta:
        model = Target


class TicketFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    message = Faker("text", locale="ru_RU")
    status = Order.Status.SUCCESS

    class Meta:
        model = Ticket
