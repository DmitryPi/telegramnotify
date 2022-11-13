from collections import namedtuple

from environ import Env
from requests_html import HTMLSession

from .models import Target


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
            proj_info = Info(id=proj_id, url=proj_url)
            projects_info.append(proj_info)
        return projects_info

    def get_project_data(self, info: (int, str)) -> namedtuple:
        """GET project page data => build data => return Data()"""
        # init named tuple
        Data = namedtuple(
            "Data", ["id", "url", "title", "body", "budget", "deadline", "sent"]
        )
        # create session
        session = HTMLSession()
        response = session.get(info.url)
        # parse html
        title = response.html.find(".b-page__title", first=True).text.lower()
        body = (
            response.html.find(f"#projectp{info.id}", first=True)
            .text.replace("\n", " ")
            .lower()
        )
        budget_deadline = response.html.find(".b-layout__txt span.b-layout__bold")
        budget = budget_deadline[0].text.lower() if len(budget_deadline) >= 1 else ""
        deadline = budget_deadline[1].text.lower() if len(budget_deadline) >= 2 else ""
        # build data
        project_data = Data(
            id=info.id,
            url=info.url,
            title=title,
            body=body,
            budget=budget,
            deadline=deadline,
            sent=False,
        )
        return project_data

    def save_project_data(self, data: namedtuple) -> None:
        """Save project data if not exist"""
        pass

    def run(self):
        projects_info = self.get_projects_info()
        project_data = self.get_project_data(projects_info[5])
        print(project_data)
        self.save_project_data(project_data)
