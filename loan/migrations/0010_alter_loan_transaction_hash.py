# Generated by Django 4.1.2 on 2023-10-20 08:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "loan",
            "0009_rename_total_interest_human_loan_current_interest_human_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="loan",
            name="transaction_hash",
            field=models.CharField(max_length=68),
        ),
    ]
