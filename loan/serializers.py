import time

from rest_framework import serializers

from . import models as l_models


class Miner(serializers.ModelSerializer):

    class Meta:
        model = l_models.Miner
        fields = "__all__"


class Loan(serializers.ModelSerializer):

    class Meta:
        model = l_models.Loan
        fields = "__all__"


class SellItem(serializers.ModelSerializer):

    class Meta:
        model = l_models.SellItem
        fields = "__all__"

