from collections import namedtuple

from requests_html import HTMLSession

from telegramnotify.utils.orm import get_parser_entry, save_parser_entry

from .models import Service


class FLParser:
    def __init__(self) -> None:
        self.target = ""
        self.source = ""
        self.set_target_source()

    def set_target_source(self) -> None:
        """Fl.ru service - https://www.fl.ru/projects/"""
        try:
            service = Service.objects.get(title="FL.ru")
            self.target = service
            self.source = service.title
        except Service.DoesNotExist as e:
            raise e

    def get_projects_info(self) -> list[tuple[int, str]]:
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

    def get_project_data(self, info: tuple[int, str]) -> namedtuple:
        """GET project page data => build data => return Data()"""
        # init named tuple
        Data = namedtuple(
            "Data",
            [
                "pid",
                "url",
                "title",
                "description",
                "budget",
                "deadline",
                "source",
                "sent",
            ],
        )
        # skip if object already exist - prevent target request
        pid = f"{self.source}-{info.id}"
        if get_parser_entry(pid):
            return
        # create session
        session = HTMLSession()
        response = session.get(info.url)
        # parse html
        title = response.html.find(".b-page__title", first=True).text.capitalize()
        try:
            description = response.html.find(
                f"#projectp{info.id}", first=True
            ).text.replace("\n", " ")
        except AttributeError:
            description = response.html.find(
                ".b-layout__txt.b-layout__txt_padbot_20", first=True
            ).text.replace("\n", " ")
        budget_deadline = response.html.find(".b-layout__txt span.b-layout__bold")
        budget = budget_deadline[0].text.lower() if len(budget_deadline) >= 1 else ""
        deadline = (
            budget_deadline[1].text.lower()
            if len(budget_deadline) >= 2
            else "по договоренности"
        )
        # build data
        project_data = Data(
            pid=pid,
            url=info.url,
            title=title,
            description=description,
            budget=budget,
            deadline=deadline,
            source=self.source,
            sent=False,
        )
        return project_data

    def run(self) -> None:
        projects_info = self.get_projects_info()
        for info in projects_info:
            project_data = self.get_project_data(info)
            save_parser_entry(project_data)
