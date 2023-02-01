import time
from datetime import datetime

from . import models as l_models
from . import serializers as l_serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from django.db.transaction import atomic


class Miner(viewsets.ModelViewSet):
    queryset = l_models.Miner.objects.all()
    serializer_class = l_serializers.Miner

    permission_classes = []

    filterset_fields = ("owner", "is_list")
    ordering_fields = ("list_time", )

    @atomic
    @action(methods=["post"], detail=True, url_path="buy")
    def c_buy(self, request, *args, **kwargs):
        serializer = l_serializers.ListMinerBuy(data=request.data)
        serializer.is_valid(raise_exception=True)
        miner = self.get_object()
        miner.is_list = False
        miner.save()
        serializer = self.get_serializer(miner)
        return Response(serializer.data)

    @atomic
    @action(methods=["post"], detail=True, url_path="list")
    def c_list(self, request, *args, **kwargs):
        serializer = l_serializers.ListMinerArgs(data=request.data)
        serializer.is_valid(raise_exception=True)
        miner = self.get_object()
        miner.is_list = True
        miner.price = serializer.validated_data["price"]
        miner.save()
        serializer = self.get_serializer(miner)
        return Response(serializer.data)

    @atomic
    @action(methods=["post"], detail=True, url_path="cancel-list")
    def c_cancel_list(self, request, *args, **kwargs):
        miner = self.get_object()
        miner.is_list = False
        miner.is_list = False
        miner.price = 0
        miner.save()
        serializer = self.get_serializer(miner)
        return Response(serializer.data)


class ListMiner(viewsets.ModelViewSet):
    queryset = l_models.ListMiner.objects.all()
    serializer_class = l_serializers.ListMiner

    permission_classes = []

    @atomic
    @action(methods=["post"], detail=True, url_path="buy")
    def c_buy(self, request, *args, **kwargs):
        serializer = l_serializers.ListMinerBuy(data=request.data)
        serializer.is_valid(raise_exception=True)
        list_miner = self.get_object()
        list_miner.delete()
        # order = l_models.Order.objects.create(
        #     seller=list_miner.seller,
        #     buyer=serializer.validated_data["buyer"],
        #     price=list_miner.price,
        #     time=time.time()
        # )
        # order_serializer = l_serializers.Order(instance=order)
        # return Response(data=order_serializer.data)
        return Response({})


class Order(viewsets.ModelViewSet):
    queryset = l_models.Order.objects.all()
    serializer_class = l_serializers.Order

    permission_classes = []
