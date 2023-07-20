from django.db import models


class Miner(models.Model):
    miner_id = models.BigIntegerField(primary_key=True, db_index=True)
    owner = models.CharField(max_length=200)
    is_list = models.BooleanField(default=False, db_index=True)
    price = models.FloatField(default=0, db_index=True)
    price_raw = models.CharField(max_length=50, blank=True, default="")
    balance_human = models.FloatField(default=0, db_index=True)
    power_human = models.FloatField(default=0, db_index=True)
    list_time = models.BigIntegerField(default=1675156423, db_index=True)
    buyer = models.CharField(max_length=42, default="0x0000000000000000000000000000000000000000")
    is_submitted_transfer_out = models.BooleanField(default=False)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        try:
            miner_price = MinerPrice.objects.get(miner_id=self.miner_id)
        except MinerPrice.DoesNotExist:
            MinerPrice.objects.create(miner_id=self.miner_id, price_human=self.price)
        else:
            miner_price.price_human = self.price
            miner_price.save()
        # MinerPrice.objects.get_or_create(miner_id=self.miner_id, price_human=self.price)
        super().save(*args, **kwargs)


class ListMiner(models.Model):
    miner_id = models.CharField(max_length=20, primary_key=True)
    owner = models.CharField(max_length=42)
    price = models.IntegerField()
    list_time = models.BigIntegerField()


class Order(models.Model):
    transaction_hash = models.CharField(max_length=66, unique=True)
    miner_id = models.BigIntegerField(db_index=True)
    seller = models.CharField(max_length=42, db_index=True)
    buyer = models.CharField(max_length=42, db_index=True)
    price_human = models.FloatField()
    balance_human = models.FloatField(default=0)
    power_human = models.FloatField(default=0)
    time = models.DateTimeField(auto_now_add=True, db_index=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class Tag(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=100)


class Comment(models.Model):
    user = models.CharField(max_length=42)
    miner = models.ForeignKey(Miner, on_delete=models.CASCADE, db_index=True)
    content = models.TextField(max_length=100)

    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    update_time = models.DateTimeField(auto_now=True)


class MinerPrice(models.Model):
    miner_id = models.IntegerField(unique=True)
    price_human = models.FloatField()