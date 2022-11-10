import json
from unittest import TestCase

from ..users import PremiumStatus, UserRole, build_user


class TestUsers(TestCase):
    def setUp(self):
        self.user_tg = {
            "is_bot": False,
            "username": "DmitrydevPy",
            "first_name": "Dmitry",
            "id": 5156307333,
            "language_code": "ru",
        }
        self.user_data = {
            "service": ["Fl.ru"],
            "words": ["test", "parse", "bot"],
        }

    def test_build_user_data(self):
        user = build_user(self.user_tg, self.user_data)
        assert user.uid == self.user_tg["id"]
        assert user.username == self.user_tg["username"]
        assert user.first_name == self.user_tg["first_name"]
        assert user.role == UserRole.USER.value
        assert user.services == json.dumps(self.user_data["service"])
        assert user.words == json.dumps(self.user_data["words"])
        assert user.bill == 0.0
        assert user.wallet == 0.0
        assert user.premium_status == PremiumStatus.TRIAL.value
        assert isinstance(user.premium_expire, str)
        assert isinstance(user.created, str)

    def test_build_user_data_admin(self):
        user = build_user(self.user_tg, self.user_data, admin=True)
        assert user.uid == self.user_tg["id"]
        assert user.username == self.user_tg["username"]
        assert user.first_name == self.user_tg["first_name"]
        assert user.role == UserRole.ADMIN.value
        assert user.services == json.dumps(self.user_data["service"])
        assert user.words == json.dumps(self.user_data["words"])
        assert user.bill == 0.0
        assert user.wallet == 0.0
        assert user.premium_status == PremiumStatus.TRIAL.value
        assert isinstance(user.premium_expire, str)
        assert isinstance(user.created, str)
