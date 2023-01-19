from config import celery_app
from telegramnotify.utils.orm import save_parser_entry

from .bots import FLParser


@celery_app.task(bind=True)
def parse_flru_task(self):
    """
    Init parser
    Parse fl.ru projects from /projects page
    Visit each project
    save parser entry
    """
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
