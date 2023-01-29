from django.db import models


class User(models.Model):
    name = models.CharField(max_length=20)


class Miner(models.Model):
    miner_id = models.CharField(max_length=20)
    owner = models.CharField(max_length=42)


class ListMiner(models.Model):
    miner_id = models.CharField(max_length=20)
    owner = models.CharField(max_length=42)
    price = models.IntegerField()
    list_time = models.DateTimeField()

