# Generated by Django 4.1.2 on 2023-02-02 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spex', '0003_order_miner_is_list_miner_list_time_miner_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='miner',
            name='owner',
            field=models.CharField(max_length=200),
        ),
    ]
