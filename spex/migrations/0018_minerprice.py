# Generated by Django 4.1.2 on 2023-07-20 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spex', '0017_alter_comment_create_time_alter_miner_balance_human_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MinerPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('miner_id', models.IntegerField(unique=True)),
                ('price_human', models.FloatField()),
            ],
        ),
    ]