import json
from dataclasses import dataclass
from enum import Enum

from .utils import datetime_days_ahead


class UserRole(Enum):
    USER = "Пользователь"
    ADMIN = "Админ"


class PremiumStatus(Enum):
    TRIAL = "Пробный период"
    GENERIC = "Обычный"
    GIGAPREMIUM = "ГИГАПремиум"
    INACTIVE = "Приостановлен"


@dataclass
class User:
    uid: int
    username: str
    first_name: str
    role: UserRole
    services: str  # json list
    words: str  # json list
    bill: float
    wallet: float
    premium_status: PremiumStatus
    premium_expire: str
    created: str


def build_user(tg_user: object, user_data: dict, admin=False) -> User:
    """tg_user - объект телеграм пользователя; user_data - telegram dict context"""
    username = tg_user["username"] if tg_user["username"] else tg_user["first_name"]
    user_role = UserRole.ADMIN.value if admin else UserRole.USER.value
    user = User(
        tg_id=tg_user["id"],
        username=username,
        first_name=tg_user["first_name"],
        role=user_role,
        services=json.dumps(user_data["service"]),
        words=json.dumps(user_data["words"]),
        bill=0.0,
        wallet=0.0,
        premium_status=PremiumStatus.TRIAL.value,
        premium_expire=str(datetime_days_ahead(3)),
    )
    return user
