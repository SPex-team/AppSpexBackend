from django.db import models


class Miner(models.Model):
    miner_id = models.CharField(max_length=20, primary_key=True)
    owner = models.CharField(max_length=42)
    is_list = models.BooleanField(default=False)
    price = models.IntegerField(default=0)
    list_time = models.BigIntegerField(default=1675156423)


class ListMiner(models.Model):
    miner_id = models.CharField(max_length=20, primary_key=True)
    owner = models.CharField(max_length=42)
    price = models.IntegerField()
    list_time = models.BigIntegerField()


class Order(models.Model):
    seller = models.CharField(max_length=42)
    buyer = models.CharField(max_length=42)
    price = models.IntegerField()
    time = models.BigIntegerField()


