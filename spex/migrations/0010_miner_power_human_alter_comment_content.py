# Generated by Django 4.1.2 on 2023-06-08 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spex', '0009_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='miner',
            name='power_human',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=models.TextField(max_length=100),
        ),
    ]