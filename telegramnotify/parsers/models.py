import uuid as uuid_lib

from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class ParserEntry(TimeStampedModel):
    """Parser record"""

    # fields
    pid = models.CharField(
        _("Project ID"),
        max_length=100,
        db_index=True,
        editable=False,
        default=uuid_lib.uuid4,
    )
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), blank=True)
    budget = models.CharField(_("Budget"), max_length=55)
    deadline = models.CharField(_("Deadline"), max_length=55)
    url = models.URLField(_("URL"), max_length=200)
    source = models.CharField(_("Source"), max_length=55)
    sent = models.BooleanField(_("Sent"), default=False)

    class Meta:
        verbose_name = _("Entry")
        verbose_name_plural = _("Entries")

    def __str__(self):
        return f"{self.source} : {self.title}"

    @property
    def short_title(self, len=40):
        return self.title[:len]
