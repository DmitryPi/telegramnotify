import re

import pytest
from django.test import TestCase

from telegramnotify.core.tests.factories import ServiceFactory

from ..bots import FLParser


class TestFLParser(TestCase):
    def setUp(self):
        self.target = ServiceFactory()
        self.fl_parser = FLParser()
        self.projects_info = self.fl_parser.get_projects_info()

    def test_init(self):
        assert self.fl_parser.target == self.target
        assert self.fl_parser.source == "FL.ru"

    @pytest.mark.slow
    def test_get_projects_info(self):
        self.projects_info = self.fl_parser.get_projects_info()
        assert len(self.projects_info) > 10
        assert isinstance(self.projects_info, list)
        for info in self.projects_info:
            assert info.id
            assert isinstance(info.id, int)
            assert info.url
            assert isinstance(info.url, str)

    @pytest.mark.slow
    def test_get_project_data(self):
        data = self.fl_parser.get_project_data(self.projects_info[10])
        assert len(data) == 8
        assert re.match(r"^(.*)-(\d+)$", data.pid)  # match Fl.ru-123
        assert "https" in data.url
        assert len(data.title) > 1
        assert len(data.description) > 1
        assert len(data.budget) > 1
        assert len(data.deadline) > 1
        assert data.source == self.fl_parser.source
        assert not data.sent
