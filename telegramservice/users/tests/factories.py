from collections.abc import Sequence
from typing import Any

from django.contrib.auth import get_user_model
from django.utils import timezone
from factory import Faker, post_generation
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyInteger

from ..models import User


class UserFactory(DjangoModelFactory):
    tg_id = FuzzyInteger(1, 11111111)
    username = Faker("user_name")
    email = Faker("email")
    name = Faker("name")
    premium_status = FuzzyChoice(
        choices=[
            User.PremiumStatus.expired,
            User.PremiumStatus.trial,
            User.PremiumStatus.regular,
            User.PremiumStatus.permanent,
        ]
    )
    premium_expire = timezone.now()

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)

    class Meta:
        model = get_user_model()
        django_get_or_create = ["username"]
