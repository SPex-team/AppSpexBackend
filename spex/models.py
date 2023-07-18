from django.db import models


class Miner(models.Model):
    miner_id = models.BigIntegerField(primary_key=True)
    owner = models.CharField(max_length=200)
    is_list = models.BooleanField(default=False)
    price = models.FloatField(default=0)
    price_raw = models.CharField(max_length=50, blank=True, default="")
    balance_human = models.FloatField(default=0)
    power_human = models.FloatField(default=0)
    list_time = models.BigIntegerField(default=1675156423)
    buyer = models.CharField(max_length=42, default="0x0000000000000000000000000000000000000000")

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class ListMiner(models.Model):
    miner_id = models.CharField(max_length=20, primary_key=True)
    owner = models.CharField(max_length=42)
    price = models.IntegerField()
    list_time = models.BigIntegerField()


class Order(models.Model):
    miner_id = models.BigIntegerField()
    seller = models.CharField(max_length=42)
    buyer = models.CharField(max_length=42)
    price_human = models.FloatField()
    balance_human = models.FloatField()
    power_human = models.FloatField()
    time = models.DateTimeField()

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class Tag(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=100)


class Comment(models.Model):
    user = models.CharField(max_length=42)
    miner = models.ForeignKey(Miner, on_delete=models.CASCADE)
    content = models.TextField(max_length=100)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
