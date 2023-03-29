import logging
import time
from datetime import datetime

from . import models as l_models
from . import serializers as l_serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import exceptions

from django.db.transaction import atomic
from django.conf import settings

from . import tasks as l_tasks
from .others.filecoin import FilecoinClient
from .others.keytool import Keytool

from . import filters as l_filters
from django_filters.rest_framework import DjangoFilterBackend


logger = logging.getLogger(__name__)


class Miner(viewsets.ModelViewSet):
    queryset = l_models.Miner.objects.all()
    serializer_class = l_serializers.Miner

    permission_classes = []

    # filter_class = l_filters.Miner
    filterset_fields = ("owner", "is_list")
    ordering_fields = ("list_time", )

    @atomic
    @action(methods=["post"], detail=True, url_path="update")
    def c_update(self, request, *args, **kwargs):
        miner = self.get_object()
        try:
            l_tasks.update_miner(miner)
        except Exception as exc:
            raise exceptions.ParseError(f"Failed to update miner: {exc}")
        serializer = l_serializers.Miner(miner)
        # data = {
        #     "details": "OK"
        # }
        return Response(serializer.data)

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


    # @atomic
    # @action(methods=["post"], detail=False, url_path="test")
    # def c_test(self, request, *args, **kwargs):
    #     l_tasks.sync_miner()
    #     data = {
    #         "details": "OK"
    #     }
    #     return Response(data)


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


class Message(viewsets.GenericViewSet):

    permission_classes = []

    @action(methods=["post"], detail=False, url_path="build-change-owner-in")
    def c_build_change_owner_in(self, request, *args, **kwargs):
        params_serializer = l_serializers.BuildChangeOwnerIn(data=request.data)
        params_serializer.is_valid(raise_exception=True)
        filecoin_client = FilecoinClient(settings.ETH_HTTP_PROVIDER)
        miner_id = params_serializer.validated_data['miner_id']
        miner_id_str = f"t0{miner_id}"
        try:
            miner_info = filecoin_client.get_miner_info(miner_id=miner_id)
        except Exception as exc:
            logger.debug(f"get miner {miner_id} info error: {exc}")
            raise exceptions.ParseError(f"get miner info error: {exc}")
        try:
            keytool = Keytool(settings.KEY_TOOL_PATH)
        except Exception as exc:
            logger.debug(f"Build miner {miner_id} message error: {exc}")
            raise exceptions.ParseError(f"Build message error: {exc}")
        msg_cid_hex, msg_cid_str, msg_hex, msg_detail = keytool.build_message(miner_info["Owner"], miner_id_str, f'"{settings.SPEX_CONTRACT_T0_ADDRESS}"')
        data = {
            "msg_cid_hex": msg_cid_hex,
            "msg_cid_str": msg_cid_str,
            "msg_hex": msg_hex,
            "msg_detail": msg_detail,
            "miner_info": miner_info
        }
        return Response(data)

    @action(methods=["post"], detail=False, url_path="build-change-owner-out")
    def c_build_change_owner_out(self, request, *args, **kwargs):
        params_serializer = l_serializers.BuildChangeOwnerOut(data=request.data)
        params_serializer.is_valid(raise_exception=True)
        miner_id = params_serializer.validated_data['miner_id']
        miner_id_str = f"t0{miner_id}"
        new_owner_address = params_serializer.validated_data["new_owner_address"]
        try:
            keytool = Keytool(settings.KEY_TOOL_PATH)
        except Exception as exc:
            logger.debug(f"Build miner {miner_id} message error: {exc}")
            raise exceptions.ParseError(f"Build message error: {exc}")
        msg_cid_hex, msg_cid_str, msg_hex, msg_detail = keytool.build_message(new_owner_address, miner_id_str, f'"{new_owner_address}"')
        data = {
            "msg_cid_hex": msg_cid_hex,
            "msg_cid_str": msg_cid_str,
            "msg_hex": msg_hex,
            "msg_detail": msg_detail,
        }
        return Response(data)

    @action(methods=["post"], detail=False, url_path="push")
    def c_push_message(self, request, *args, **kwargs):
        params_serializer = l_serializers.PushMessage(data=request.data)
        params_serializer.is_valid(raise_exception=True)
        keytool = Keytool(settings.KEY_TOOL_PATH)
        message = params_serializer.validated_data["message"]
        sign = params_serializer.validated_data["sign"]
        try:
            # keytool.push_message_spex(message=message, sign=sign)
            time.sleep(10)
        except Exception as exc:
            logger.debug(f"Push message error, message: {message} sign: {sign}")
            raise exceptions.ParseError(f"Push message error: {exc}")
        data = {}
        if params_serializer.validated_data["wait"]:
            cid = params_serializer.validated_data["cid"]
            filecoin_client = FilecoinClient(settings.ETH_HTTP_PROVIDER)
            try:
                filecoin_client.wait_message(cid)
            except Exception as exc:
                logger.debug(f"wait message error, cid: {cid} exc: {exc}")
        return Response(data)

    # @action(methods=["post"], detail=False, url_path="push-wait")
    # def c_push_wait_message(self, request, *args, **kwargs):
    #     pass



