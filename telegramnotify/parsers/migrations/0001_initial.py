# Generated by Django 4.1.3 on 2023-01-19 07:42

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ParserEntry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "pid",
                    models.CharField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        max_length=100,
                        verbose_name="Project ID",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="Title")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                ("budget", models.CharField(max_length=55, verbose_name="Budget")),
                ("deadline", models.CharField(max_length=55, verbose_name="Deadline")),
                ("url", models.URLField(verbose_name="URL")),
                ("source", models.CharField(max_length=55, verbose_name="Source")),
                ("sent", models.BooleanField(default=False, verbose_name="Sent")),
            ],
            options={
                "verbose_name": "Entry",
                "verbose_name_plural": "Entries",
            },
        ),
    ]
