# Generated by Django 4.1.2 on 2023-10-18 07:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("loan", "0005_loanoperatorrecord_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="loanitem",
            name="annual_interest_rate_raw",
        ),
    ]
