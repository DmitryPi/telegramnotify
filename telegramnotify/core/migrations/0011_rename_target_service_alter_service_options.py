# Generated by Django 4.0.8 on 2022-11-16 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_target_daily_price"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Target",
            new_name="Service",
        ),
        migrations.AlterModelOptions(
            name="service",
            options={"verbose_name": "Service", "verbose_name_plural": "Services"},
        ),
    ]
