import re
from collections import namedtuple

from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import ParserEntry

User = get_user_model()


def datetime_days_ahead(days: int) -> timezone:
    now = timezone.now()
    delta = timezone.timedelta(days=days)
    return now + delta


def search_word(text: str, word: str) -> re.Match:
    """Search whole word in text"""
    return re.search(rf"\b{word}\b", text, re.IGNORECASE)


def get_parser_entry(pid: str) -> ParserEntry:
    """Get parser_entry or None"""
    try:
        parser_entry = ParserEntry.objects.get(pid=pid)
        return parser_entry
    except ParserEntry.DoesNotExist:
        return None


def get_parser_entries() -> [ParserEntry]:
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


def update_parser_entries_sent(entries: [ParserEntry]) -> None:
    """Update field sent=True on given ParserEntry objects"""
    for entry in entries:
        entry.sent = True
        entry.save(update_fields=["sent"])


def get_users_all() -> [User]:
    """Get all users"""
    users = User.objects.all()
    return users


def get_users() -> [User]:
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


def users_update_premium_expired() -> None:
    """
    Loop through users
    Skip users with premium_status=permanent
    Check if premium_expire date passed
        set premium_status=expired
    """
    users = get_users()
    for user in users:
        if user.premium_status == User.PremiumStatus.permanent:
            continue
        if timezone.now() > user.premium_expire:
            user.premium_status = User.PremiumStatus.expired
            user.save(update_fields=["premium_status"])
