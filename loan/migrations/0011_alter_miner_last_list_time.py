# Generated by Django 4.1.2 on 2023-10-26 06:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("loan", "0010_alter_loan_transaction_hash"),
    ]

    operations = [
        migrations.AlterField(
            model_name="miner",
            name="last_list_time",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
