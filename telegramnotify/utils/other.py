import re

from django.utils import timezone


def list_into_chunks(lst: list, n: int = 2) -> list[list]:
    """Split list into chunks [1, 2, 3] => [[1, 2], [3]]"""
    result = [lst[i : i + n] for i in range(0, len(lst), n)]  # noqa skip
    return result


def datetime_days_ahead(days: int) -> timezone:
    now = timezone.now()
    delta = timezone.timedelta(days=days)
    return now + delta


def search_word(text: str, word: str) -> re.Match:
    """Search whole word in text"""
    return re.search(rf"\b{word}\b", text, re.IGNORECASE)
