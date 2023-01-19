from django.test import TestCase

from ..models import Ticket
from .factories import TicketFactory


class TestTicket(TestCase):
    def setUp(self):
        self.batch_size = 10
        self.objects = TicketFactory.create_batch(size=self.batch_size)

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
        qs = Ticket.objects.all()
        assert not len(qs)

    def test_fields(self):
        for obj in self.objects:
            assert obj.user.id
            assert len(obj.message) > 1
            assert isinstance(obj.status, Ticket.Status)
            assert len(obj.short_message) > 1
