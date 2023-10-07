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

from devops_django import mixins as dd_mixins

logger = logging.getLogger(__name__)


class Miner(dd_mixins.AggregationMixin, viewsets.ModelViewSet):
    queryset = l_models.Miner.objects.all()
    serializer_class = l_serializers.Miner

    permission_classes = []

    filterset_fields = ("miner_id", "delegator_address", "receive_address", "disabled")
    ordering_fields = ("miner_id", "max_debt_amount_human", "loan_day_rate_human", "last_debt_amount_human",
                       "last_update_timestamp", "create_time")
    search_fields = ("miner_id", )


class Loan(dd_mixins.AggregationMixin, viewsets.ModelViewSet):
    queryset = l_models.Loan.objects.all()
    serializer_class = l_serializers.Loan

    permission_classes = []

    filterset_fields = ("miner_id", "user_address")
    ordering_fields = ("miner_id", "last_amount_human", "last_update_timestamp", "create_time")
    search_fields = ("miner_id", "user_address")
