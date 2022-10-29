from unittest import TestCase

from ..users import UserRole, build_user


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
        assert isinstance(user.created, str)
        assert isinstance(user.updated, str)
