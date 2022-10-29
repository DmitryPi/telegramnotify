from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    USER = "Пользователь"
    ADMIN = "Админ"


@dataclass
class User:
    uid: int
    username: str
    first_name: str
    role: UserRole
    created: str
    updated: str


def build_user(tg_data: dict, admin=False) -> User:
    """user_data - из json файла; tg_data - объект телеграм пользователя"""
    now = str(datetime.now())
    username = tg_data["username"] if tg_data["username"] else tg_data["first_name"]
    user_role = UserRole.ADMIN.value if admin else UserRole.USER.value
    user = User(
        tg_data["id"],
        username,
        tg_data["first_name"],
        user_role,
        now,
        now,
    )
    return user
