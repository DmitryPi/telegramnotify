# Generated by Django 4.1.3 on 2023-01-20 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_alter_user_services"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="bill",
        ),
        migrations.AddField(
            model_name="user",
            name="pay_rate",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=11, verbose_name="Ставка Оплаты"
            ),
        ),
    ]
