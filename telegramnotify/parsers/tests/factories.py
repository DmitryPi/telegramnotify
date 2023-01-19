import random

from factory import Faker, LazyAttribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

from ..models import ParserEntry


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
