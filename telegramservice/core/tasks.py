import time

from django_celery_beat.models import PeriodicTask

from config import celery_app

from .parsers import FLParser, SenderBot
from .utils import save_parser_entry


@celery_app.task(ignore_result=True)
def clean_oneoff_tasks():
    """Clean oneoff tasks with enabled=False"""
    PeriodicTask.objects.filter(one_off=True, enabled=False).delete()


@celery_app.task(bind=True)
def parse_flru_task(self):
    parser = FLParser()
    projects_info = parser.get_projects_info()
    for i, info in enumerate(projects_info):
        # update task progress
        self.update_state(
            state="PROGRESS", meta={"current": i, "total": len(projects_info)}
        )
        # get data => save data
        project_data = parser.get_project_data(info)
        save_parser_entry(project_data)


@celery_app.task(bind=True)
def sender_bot_task(self):
    sender_bot = SenderBot()
    sender_bot.run()


@celery_app.task(bind=True)
def long_running_task(self):
    for i in range(50):
        self.update_state(state="PROGRESS", meta={"current": i, "total": 50})
        self.args = "test"
        print(i)
        print(self.AsyncResult(self.request.id).state)
        time.sleep(1)
