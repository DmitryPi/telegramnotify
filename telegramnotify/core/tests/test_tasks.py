import pytest
from celery.result import EagerResult
from django.contrib.auth import get_user_model
from django.utils import timezone
from factory.fuzzy import FuzzyChoice

from telegramnotify.users.tests.factories import UserFactory
from telegramnotify.utils.orm import get_users_exclude_expired

from ..tasks import users_update_premium_expired_task

User = get_user_model()


@pytest.mark.django_db
def test_users_update_premium_expired_task(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    UserFactory.create_batch(
        10, premium_expire=timezone.now() - timezone.timedelta(hours=1)
    )
    result = users_update_premium_expired_task.delay()
    users = User.objects.all()
    assert isinstance(result, EagerResult)
    for user in users:
        if user.premium_status == User.PremiumStatus.permanent:
            assert user.premium_status == User.PremiumStatus.permanent
        else:
            assert user.premium_status == User.PremiumStatus.expired


@pytest.mark.django_db
def test_users_update_premium_expired_with_trial_or_regular_task(settings):
    """Test update for premium_status of trial and regular"""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    hour_before = timezone.now() - timezone.timedelta(hours=1)
    hour_ahead = timezone.now() + timezone.timedelta(hours=1)
    # hour before
    UserFactory.create_batch(
        20,
        premium_status=FuzzyChoice(
            [User.PremiumStatus.trial, User.PremiumStatus.regular]
        ),
        premium_expire=hour_before,
    )
    # hour ahead
    UserFactory.create_batch(
        10,
        premium_status=FuzzyChoice(
            [User.PremiumStatus.trial, User.PremiumStatus.regular]
        ),
        premium_expire=hour_ahead,
    )
    users = get_users_exclude_expired()
    assert len(users) == 30
    result = users_update_premium_expired_task.delay()
    users = get_users_exclude_expired()
    assert len(users) == 10
    assert isinstance(result, EagerResult)
    for user in users:
        assert timezone.now() < user.premium_expire


@pytest.mark.django_db
def test_users_update_premium_expired_with_permanent_task(settings):
    """
    Test if permanent users are exluded from evaluation
    Even if for some reason permanent_status date passed,
    Permanent status won't be changed
    """
    settings.CELERY_TASK_ALWAYS_EAGER = True
    hour_before = timezone.now() - timezone.timedelta(hours=1)
    UserFactory.create_batch(
        10,
        premium_status=User.PremiumStatus.permanent,
        premium_expire=hour_before,
    )
    users = get_users_exclude_expired()
    assert len(users) == 10
    result = users_update_premium_expired_task.delay()
    users = get_users_exclude_expired()
    assert len(users) == 10
    assert isinstance(result, EagerResult)
    for user in users:
        assert user.premium_status == User.PremiumStatus.permanent
        assert timezone.now() > user.premium_expire
