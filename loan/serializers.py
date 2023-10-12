import time

from rest_framework import serializers

from . import models as l_models


class LoanMiner(serializers.ModelSerializer):

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


class LoanComment(serializers.ModelSerializer):

    def validate_user(self, value):
        return value.lower()

    class Meta:
        model = l_models.Comment
        fields = "__all__"
