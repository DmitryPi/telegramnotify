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

    def test_build_user_data(self):
        user = build_user(self.user_tg)
        assert user.uid == self.user_tg["id"]
        assert user.username == self.user_tg["username"]
        assert user.first_name == self.user_tg["first_name"]
        assert user.role == UserRole.USER.value
        assert user.services == ""
        assert user.bill == 0.0
        assert user.wallet == 0.0
        assert user.premium_status == PremiumStatus.TRIAL.value
        assert isinstance(user.premium_expire, str)
        assert isinstance(user.created, str)

    def test_build_user_data_admin(self):
        user = build_user(self.user_tg, admin=True)
        assert user.uid == self.user_tg["id"]
        assert user.username == self.user_tg["username"]
        assert user.first_name == self.user_tg["first_name"]
        assert user.role == UserRole.ADMIN.value
        assert user.services == ""
        assert user.bill == 0.0
        assert user.wallet == 0.0
        assert user.premium_status == PremiumStatus.TRIAL.value
        assert isinstance(user.premium_expire, str)
        assert isinstance(user.created, str)
