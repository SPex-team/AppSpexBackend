# Generated by Django 4.1.2 on 2023-03-21 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spex', '0005_tag_alter_miner_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='miner',
            name='miner_id',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
    ]
