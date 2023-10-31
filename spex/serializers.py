import time

from rest_framework import serializers

from . import models as l_models


class Miner(serializers.ModelSerializer):

    class Meta:
        model = l_models.Miner
        fields = "__all__"


class ListMiner(serializers.ModelSerializer):

    class Meta:
        model = l_models.ListMiner
        fields = "__all__"


class Order(serializers.ModelSerializer):

    class Meta:
        model = l_models.Order
        fields = "__all__"


class Comment(serializers.ModelSerializer):

    def validate_user(self, value):
        return value.lower()

    class Meta:
        model = l_models.Comment
        fields = "__all__"


class ListMinerBuy(serializers.Serializer):
    buyer = serializers.CharField(max_length=42)


class ListMinerArgs(serializers.Serializer):
    price = serializers.IntegerField()


class BuildChangeOwnerIn(serializers.Serializer):
    miner_id = serializers.IntegerField()
    to_address = serializers.IntegerField(default=None, allow_null=True)


class BuildChangeBeneficiaryIn(serializers.Serializer):
    miner_id = serializers.IntegerField()
    to_address = serializers.IntegerField(default=None, allow_null=True)


class BuildChangeOwnerOut(serializers.Serializer):
    miner_id = serializers.IntegerField()
    new_owner_address = serializers.CharField()


class BuildChangeBeneficiaryOut(serializers.Serializer):
    miner_id = serializers.IntegerField()
    new_beneficiary = serializers.CharField()
    new_quota = serializers.CharField()
    new_expiration = serializers.IntegerField()


class PushMessage(serializers.Serializer):
    message = serializers.CharField()
    sign = serializers.CharField()
    cid = serializers.CharField()
    wait = serializers.BooleanField()

