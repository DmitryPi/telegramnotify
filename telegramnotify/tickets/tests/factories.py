from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

from telegramnotify.users.tests.factories import UserFactory

from ..models import Ticket


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
