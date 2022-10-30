from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .utils import datetime_days_ahead


class UserRole(Enum):
    USER = "Пользователь"
    ADMIN = "Админ"


class PremiumStatus(Enum):
    TRIAL = "Trial"
    GENERIC = "Generic"
    GIGAPREMIUM = "GIGAPremium"


@dataclass
class User:
    uid: int
    username: str
    first_name: str
    role: UserRole
    bill: float
    wallet: float
    services: str  # json field
    premium_status: PremiumStatus
    premium_expire: str
    created: str


def build_user(tg_data: dict, admin=False) -> User:
    """user_data - из json файла; tg_data - объект телеграм пользователя"""
    username = tg_data["username"] if tg_data["username"] else tg_data["first_name"]
    user_role = UserRole.ADMIN.value if admin else UserRole.USER.value
    user = User(
        uid=tg_data["id"],
        username=username,
        first_name=tg_data["first_name"],
        role=user_role,
        services="",
        bill=0.0,
        wallet=0.0,
        premium_status=PremiumStatus.TRIAL.value,
        premium_expire=str(datetime_days_ahead(3)),
        created=str(datetime.now()),
    )
    return user
