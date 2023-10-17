import logging
import time
from datetime import datetime

import web3.constants

from . import models as l_models
from . import serializers as l_serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import exceptions
from rest_framework import mixins
from rest_framework import status

from django.db.transaction import atomic
from django.conf import settings

from devops_django import decorators as dd_decorators

from web3 import Account
from eth_account.messages import encode_defunct

from . import filters as l_filters
from . import tasks as l_tasks
from .others import task_functions as l_task_functions


from devops_django import mixins as dd_mixins

logger = logging.getLogger(__name__)


class Miner(dd_mixins.AggregationMixin, viewsets.ModelViewSet):
    queryset = l_models.Miner.objects.all()
    serializer_class = l_serializers.LoanMiner

    permission_classes = []

    filterset_fields = ("miner_id", "delegator_address", "receive_address", "disabled")
    ordering_fields = ("miner_id", "max_debt_amount_human", "loan_day_rate_human", "last_debt_amount_human",
                       "last_update_timestamp", "create_time")
    search_fields = ("miner_id", )

    @action(methods=["get"], detail=False, url_path="transfer-in-check")
    @dd_decorators.parameter("miner_id", int)
    def c_transfer_in_check(self, request, miner_id, *args, **kwargs):
        count = l_models.Miner.objects.filter(miner_id=miner_id).count()
        if count > 0:
            raise exceptions.ParseError("miner already in SPex")
        return Response({})

    @action(methods=["get"], detail=False, url_path="balances")
    @dd_decorators.parameter("miner_id", int)
    def c_get_balances(self, request, miner_id, *args, **kwargs):
        try:
            total_balance_human, available_balance_human, pledge_balance_human, locked_balance_human = l_task_functions.\
                get_miner_balances(f"{settings.ADDRESS_PREFIX}0{miner_id}")
        except Exception as exc:
            raise exceptions.ParseError(f"Failed to get miner balances exc: {exc}")
        data = {
            "total_balance_human": total_balance_human,
            "available_balance_human": available_balance_human,
            "pledge_balance_human": pledge_balance_human,
            "locked_balance_human": locked_balance_human
        }
        return Response(data)


class Loan(dd_mixins.AggregationMixin, viewsets.ModelViewSet):
    queryset = l_models.Loan.objects.all()
    serializer_class = l_serializers.Loan

    permission_classes = []

    filterset_fields = ("miner_id", "user_address")
    ordering_fields = ("miner_id", "last_amount_human", "last_update_timestamp", "create_time")
    search_fields = ("miner_id", "user_address")


class Comment(mixins.RetrieveModelMixin,
              mixins.ListModelMixin,
              mixins.CreateModelMixin,
              mixins.DestroyModelMixin,
              viewsets.GenericViewSet):

    queryset = l_models.Comment.objects.all()
    serializer_class = l_serializers.LoanComment

    permission_classes = []

    filterset_fields = ["miner", "miner_id", "user"]
    ordering_fields = ["create_time"]
    search_fields = ("content",)

    def update_number_comments(self, miner):
        number_comments = l_models.Comment.objects.filter(miner_id=miner.miner_id).count()
        miner.number_comments = number_comments
        miner.save()

    @atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        miner = serializer.validated_data["miner"]
        self.update_number_comments(miner)
        # # number_comments = l_models.Comment.objects.filter(miner_id=miner.id).count()
        # # miner.number_comments = number_comments
        # # miner.save()

    @atomic
    def perform_destroy(self, instance):
        miner = instance.miner
        super().perform_destroy(instance)
        self.update_number_comments(miner)

    @dd_decorators.parameter("sign")
    def create(self, request, sign, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        signable_message = encode_defunct(text="Sign comment: " + serializer.validated_data["content"])
        # signable_message = + message
        recovered_address = Account.recover_message(signable_message, signature=sign)

        if recovered_address.lower() != serializer.validated_data["user"].lower():
            raise exceptions.ParseError(f"sign error, recovered_address is {recovered_address}")
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @dd_decorators.parameter("sign")
    def destroy(self, request, sign, *args, **kwargs):
        instance = self.get_object()
        sign_txt = "Delete comment: " + instance.content
        signable_message = encode_defunct(text=sign_txt)
        # signable_message = + message
        recovered_address = Account.recover_message(signable_message, signature=sign)
        if recovered_address.lower() != instance.user.lower():
            raise exceptions.ParseError(f"sign error, recovered_address is {recovered_address}")
        return super().destroy(request, *args, **kwargs)
