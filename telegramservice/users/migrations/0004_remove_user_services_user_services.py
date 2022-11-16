# Generated by Django 4.0.8 on 2022-11-16 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_rename_target_service_alter_service_options'),
        ('users', '0003_alter_user_premium_expire'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='services',
        ),
        migrations.AddField(
            model_name='user',
            name='services',
            field=models.ManyToManyField(blank=True, related_name='%(class)ss', to='core.service'),
        ),
    ]
