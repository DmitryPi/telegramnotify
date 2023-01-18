from collections import namedtuple

from django.contrib.auth import get_user_model
from django.utils import timezone

from telegramnotify.core.models import ParserEntry

User = get_user_model()


def get_parser_entry(pid: str) -> ParserEntry | None:
    """Get parser_entry or None"""
    try:
        parser_entry = ParserEntry.objects.get(pid=pid)
        return parser_entry
    except ParserEntry.DoesNotExist:
        return None


def get_parser_entries() -> list[ParserEntry]:
    """Get ParserEntry with sent=False"""
    entries = ParserEntry.objects.filter(sent=False)
    return entries


def save_parser_entry(data: namedtuple) -> None:
    """Save ParserEntry data if not exist"""
    if not data:
        return
    print("Saving: " + data.title)
    data_dict = data._asdict()
    ParserEntry.objects.get_or_create(**data_dict)


def update_parser_entries_sent(entries: list[ParserEntry]) -> None:
    """Update field sent=True on given ParserEntry objects"""
    for entry in entries:
        entry.sent = True
        entry.save(update_fields=["sent"])


def get_users_all() -> list[User]:
    """Get all users"""
    users = User.objects.all()
    return users


def get_users_exclude_expired() -> list[User]:
    """Get users and exclude those with premium_status=expired"""
    users = User.objects.exclude(premium_status=User.PremiumStatus.expired)
    return users


def user_set_status_permanent(user: User) -> None:
    """
    Update user premium_status to permanent
    Add 3650 days to premium_expire
    """
    permanent_date = timezone.now() + timezone.timedelta(days=3650)
    user.premium_status = User.PremiumStatus.permanent
    user.premium_expire = permanent_date
    user.save()
