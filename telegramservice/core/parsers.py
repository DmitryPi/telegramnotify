from collections import namedtuple

from environ import Env
from requests_html import HTMLSession

from telegramservice.core.models import Target


class FLParser:
    def __init__(self, env: Env):
        self.env = env
        self.target = ""
        self.set_target()

    def set_target(self) -> None:
        """Fl.ru target - https://www.fl.ru/projects/"""
        try:
            target = Target.objects.get(title="FL.ru")
            self.target = target
        except Target.DoesNotExist as e:
            print("Target you are trying to find DoesNotExist")
            raise e

    def get_projects_info(self) -> [(int, str)]:
        """GET target page => parse project id, build url

        >> return [Info(proj_id, proj_url)]
        """
        # init named tuple
        Info = namedtuple("Info", ["id", "url"])
        # create session
        session = HTMLSession()
        response = session.get(self.target.url_query)
        # find <a> proj link
        projects = response.html.find(".b-post__link")
        projects_info = []
        for proj in projects:
            proj_id = int(proj.attrs["href"].split("/")[2])
            # https://www.fl.ru/ + projects/<id>/<slug>
            proj_url = self.target.url_body + proj.attrs["href"][1:]
            proj_info = Info(proj_id, proj_url)
            projects_info.append(proj_info)
        return projects_info

    def get_projects_data(self) -> dict:
        """GET project page data => build data => return dict"""
        project_data = {}
        return project_data

    def save_project_data(self) -> None:
        """Save project data if not exist"""
        pass

    def run(self):
        info = self.get_projects_info()
        print(info[0].url)
