# Generated by Django 4.1.2 on 2023-01-31 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spex', '0002_remove_listminer_id_remove_miner_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seller', models.CharField(max_length=42)),
                ('buyer', models.CharField(max_length=42)),
                ('price', models.IntegerField()),
                ('time', models.BigIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='miner',
            name='is_list',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='miner',
            name='list_time',
            field=models.BigIntegerField(default=1675156423),
        ),
        migrations.AddField(
            model_name='miner',
            name='price',
            field=models.IntegerField(default=0),
        ),
    ]
