import re

from django.test import TestCase

from ..models import ParserEntry
from .factories import ParserEntryFactory


class TestParserEntry(TestCase):
    def setUp(self):
        self.batch_size = 10
        self.objects = ParserEntryFactory.create_batch(size=self.batch_size)

    def test_create(self):
        assert len(self.objects) == self.batch_size

    def test_update(self):
        new_title = "new title"
        for obj in self.objects:
            obj.title = new_title
            obj.save()
        for obj in self.objects:
            assert obj.title == new_title

    def test_delete(self):
        for obj in self.objects:
            obj.delete()
        qs = ParserEntry.objects.all()
        assert not len(qs)

    def test_fields(self):
        for obj in self.objects:
            assert re.match(r"^(.*)-(\d+)$", obj.pid)  # match Fl.ru-123
            assert len(obj.title) > 1
            assert len(obj.description) > 1
            assert obj.budget
            assert obj.deadline
            assert "https" in obj.url
            assert obj.source == "FL.ru"
            assert isinstance(obj.sent, bool)
            assert len(obj.short_title) > 1

    def test_parser_entry_str_method(self):
        entry = ParserEntryFactory(title="Test Entry", source="Test Source")
        assert str(entry) == "Test Source : Test Entry"

    def test_parser_entry_short_title(self):
        entry = ParserEntryFactory(
            title="This is a very long title that should be shortened"
        )
        assert entry.short_title == entry.title[:40]
