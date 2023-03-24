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


class ListMinerBuy(serializers.Serializer):
    buyer = serializers.CharField(max_length=42)


class ListMinerArgs(serializers.Serializer):
    price = serializers.IntegerField()


class BuildChangeOwner(serializers.Serializer):
    miner_id = serializers.IntegerField()


class PushMessage(serializers.Serializer):
    message = serializers.CharField()
    sign = serializers.CharField()
    cid = serializers.CharField()
    wait = serializers.BooleanField()

