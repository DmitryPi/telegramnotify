from django_celery_beat.models import PeriodicTask

from config import celery_app


@celery_app.task(ignore_result=True)
def clean_oneoff_tasks():
    """Clean oneoff tasks with enabled=False"""
    PeriodicTask.objects.filter(one_off=True, enabled=False).delete()
