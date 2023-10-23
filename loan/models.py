from django.db import models


class Miner(models.Model):
    miner_id = models.BigIntegerField(primary_key=True, db_index=True)
    delegator_address = models.CharField(max_length=42)
    max_debt_amount_raw = models.CharField(max_length=80, blank=True, default="0")
    max_debt_amount_human = models.FloatField(default=0, db_index=True)
    receive_address = models.CharField(max_length=42)

    # daily_interest_rate = models.FloatField(default=0)
    annual_interest_rate_human = models.FloatField(default=0)

    last_debt_amount_raw = models.CharField(max_length=80, blank=True, default="0")
    last_debt_amount_human = models.FloatField(default=0)
    last_update_timestamp = models.BigIntegerField(default=1675156423)
    disabled = models.BooleanField(default=False)

    collateral_rate = models.FloatField(default=0)

    total_balance_human = models.FloatField(default=0)
    available_balance_human = models.FloatField(default=0)
    initial_pledge_human = models.FloatField(default=0)
    locked_rewards_human = models.FloatField(default=0)

    last_list_time = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)

    current_total_debt_human = models.FloatField(default=0)
    current_total_principal_human = models.FloatField(default=0)
    current_total_interest_human = models.FloatField(default=0)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class Loan(models.Model):
    miner_id = models.BigIntegerField(db_index=True)
    user_address = models.CharField(max_length=42)

    miner_total_balance_human = models.FloatField(default=0)

    daily_interest_rate = models.FloatField(default=0)
    annual_interest_rate = models.FloatField(default=0)

    # current_principal_raw = models.CharField(max_length=80, blank=True, default="0")
    current_principal_human = models.FloatField(default=0)

    current_interest_human = models.FloatField(default=0)
    # current_total_amount_raw = models.CharField(max_length=80, blank=True, default="0")
    current_total_amount_human = models.FloatField(default=0)

    last_amount_raw = models.CharField(max_length=80, blank=True, default="0")
    last_amount_human = models.FloatField(default=0)
    last_update_timestamp = models.BigIntegerField(default=1675156423)

    transaction_hash = models.CharField(max_length=68)

    completed = models.BooleanField(default=False)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("miner_id", "user_address"),)


class SellItem(models.Model):
    miner_id = models.BigIntegerField(db_index=True)
    user_address = models.CharField(max_length=42)
    amount_raw = models.CharField(max_length=80, blank=True, default="0")
    amount_human = models.FloatField(default=0)

    price_raw = models.CharField(max_length=80, blank=True, default="0")
    price_human = models.FloatField(default=0)

    last_update_timestamp = models.BigIntegerField(default=1675156423)

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


class LoanItem(models.Model):
    miner_id = models.BigIntegerField(db_index=True)
    user_address = models.CharField(max_length=42)

    annual_interest_rate_human = models.FloatField(default=0)
    amount_raw = models.CharField(max_length=80, blank=True, default="0")
    amount_human = models.FloatField()

    time = models.DateTimeField(db_index=True)

    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    update_time = models.DateTimeField(auto_now=True)


class PaybackItem(models.Model):
    miner_id = models.BigIntegerField(db_index=True)
    user_address = models.CharField(max_length=42)

    amount_raw = models.CharField(max_length=80, blank=True, default="0")
    amount_human = models.FloatField()
    time = models.DateTimeField(db_index=True)

    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    update_time = models.DateTimeField(auto_now=True)


class LoanOperatorRecord(models.Model):
    OPERATOR_TYPE_CHOICES = [
        ("lend", "lend"),
        ("wallet_repayment", "wallet_repayment",),
        ("withdraw_repayment", "withdraw_repayment")
    ]

    miner_id = models.BigIntegerField(db_index=True)
    user_address = models.CharField(max_length=42)

    operator_user_address = models.CharField(max_length=42)

    operator_type = models.CharField(choices=OPERATOR_TYPE_CHOICES, max_length=30, db_index=True)

    amount_raw = models.CharField(max_length=80, blank=True, default="0")
    amount_human = models.FloatField()

    time = models.DateTimeField(db_index=True)

    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    update_time = models.DateTimeField(auto_now=True)
