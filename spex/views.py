import json
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
from .others.filecoin import FilecoinClient
from .others.keytool import Keytool
from .others import objects as o_objects

from devops_django import mixins as dd_mixins

logger = logging.getLogger(__name__)


class Miner(dd_mixins.AggregationMixin, viewsets.ModelViewSet):
    queryset = l_models.Miner.objects.all()
    serializer_class = l_serializers.Miner

    permission_classes = []

    filterset_fields = ("owner", "is_list", "buyer")
    ordering_fields = ("list_time", "price", "price_raw", "balance_human", "power_human")
    search_fields = ("miner_id",)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        validated_data = serializer.validated_data
        # try:
        #     miner_price = l_models.MinerPrice.objects.get(miner_id=validated_data["miner_id"])
        #     miner_price.price_human = validated_data["price"]
        #     miner_price.save()
        # except l_models.MinerPrice.DoesNotExist:
        #     l_models.MinerPrice.objects.create(miner_id=validated_data["miner_id"], price_human=validated_data["price"])
        o_objects.MinerLastInfo.update_from_miner(serializer.instance)

    @action(methods=["post"], detail=False, url_path="sync-new-miners")
    def c_sync_new_miners(self, request, *args, **kwargs):
        l_tasks.sync_new_miners()
        data = {}
        return Response(data)

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

    @action(methods=["post"], detail=True, url_path="buy")
    def c_buy(self, request, *args, **kwargs):
        serializer = l_serializers.ListMinerBuy(data=request.data)
        serializer.is_valid(raise_exception=True)
        miner = self.get_object()
        miner.is_list = False
        miner.save()
        serializer = self.get_serializer(miner)
        return Response(serializer.data)

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

    @action(methods=["post"], detail=True, url_path="cancel-list")
    def c_cancel_list(self, request, *args, **kwargs):
        miner = self.get_object()
        miner.is_list = False
        miner.price = 0
        miner.save()
        serializer = self.get_serializer(miner)
        return Response(serializer.data)

    @action(methods=["get"], detail=False, url_path="transfer-in-check")
    @dd_decorators.parameter("miner_id", int)
    def c_transfer_in_check(self, request, miner_id, *args, **kwargs):
        res_data = {
            "in_spex": False,
            "listed": False
        }
        count = l_models.Miner.objects.filter(miner_id=miner_id).count()
        if count > 0:
            raise exceptions.ParseError("miner already in SPex")
        filecoin_client = FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
        try:
            miner_info = filecoin_client.get_miner_info(miner_id)
        except Exception as exc:
            raise exceptions.ParseError(f"get miner info error: {str(exc)}")
        if miner_info["Owner"] != miner_info["Beneficiary"]:
            raise exceptions.ParseError(f"Beneficiary is not owner")

        if miner_info["PendingBeneficiaryTerm"] is not None:
            raise exceptions.ParseError(f"Pending beneficiary is not none")

        spex_contract = l_tasks.get_spex_contract()
        owner = spex_contract.functions.getMinerDelegator(miner_id).call()
        if owner != web3.constants.ADDRESS_ZERO:
            l_tasks.sync_new_miners()
            res_data["in_spex"] = True
        return Response(res_data)

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


class Order(viewsets.ReadOnlyModelViewSet):
    queryset = l_models.Order.objects.all()
    serializer_class = l_serializers.Order

    filterset_class = l_filters.Order
    # filterset_fields = ("seller", "miner_id", "buyer")
    ordering_fields = ("time", "price_human", "balance_human", "power_human", "create_time")

    permission_classes = []


class Message(viewsets.GenericViewSet):
    permission_classes = []
    serializer_class = l_serializers.BuildChangeOwnerIn

    @action(methods=["post"], detail=False, url_path="build-change-owner-in")
    def c_build_change_owner_in(self, request, *args, **kwargs):
        params_serializer = l_serializers.BuildChangeOwnerIn(data=request.data)
        params_serializer.is_valid(raise_exception=True)
        filecoin_client = FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
        miner_id = params_serializer.validated_data['miner_id']
        miner_id_str = f"{settings.ADDRESS_PREFIX}0{miner_id}"
        to_address = params_serializer.validated_data["to_address"]
        to_address = settings.SPEX_CONTRACT_T0_ADDRESS if to_address is None else to_address
        try:
            miner_info = filecoin_client.get_miner_info(miner_id=miner_id)
        except Exception as exc:
            logger.debug(f"get miner {miner_id} info error: {exc}")
            raise exceptions.ParseError(f"get miner info error: {exc}")
        keytool = Keytool(settings.KEY_TOOL_PATH)
        try:
            msg_cid_hex, msg_cid_str, msg_hex, msg_detail = keytool.build_change_owner_message(miner_info["Owner"],
                                                                                               miner_id_str,
                                                                                               f'"{to_address}"')
        except Exception as exc:
            logger.debug(f"Build miner {miner_id} message error: {exc}")
            raise exceptions.ParseError(f"Build message error: {exc}")
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
        miner_id_str = f"{settings.ADDRESS_PREFIX}0{miner_id}"
        new_owner_address = params_serializer.validated_data["new_owner_address"]
        keytool = Keytool(settings.KEY_TOOL_PATH)
        try:
            msg_cid_hex, msg_cid_str, msg_hex, msg_detail = keytool.build_change_owner_message(new_owner_address,
                                                                                               miner_id_str,
                                                                                               f'"{new_owner_address}"')
        except Exception as exc:
            logger.debug(f"Build miner {miner_id} message error: {exc}")
            raise exceptions.ParseError(f"Build message error: {exc}")
        data = {
            "msg_cid_hex": msg_cid_hex,
            "msg_cid_str": msg_cid_str,
            "msg_hex": msg_hex,
            "msg_detail": msg_detail,
        }
        return Response(data)

    @action(methods=["post"], detail=False, url_path="push")
    def c_push_message(self, request, *args, **kwargs):
        logger.debug(f"request.data: {request.data}")
        params_serializer = l_serializers.PushMessage(data=request.data)
        params_serializer.is_valid(raise_exception=True)
        keytool = Keytool(settings.KEY_TOOL_PATH)
        message = params_serializer.validated_data["message"]
        sign = params_serializer.validated_data["sign"]
        # if settings.ENV == "LOCAL":
        #     time.sleep(5)
        #     return Response({})
        try:
            keytool.push_message_spex(message=message, sign=sign)
            # time.sleep(2)
        except Exception as exc:
            logger.debug(f"Push message error, message: {message} sign: {sign}")
            raise exceptions.ParseError(f"Push message error: {exc}")
        data = {}
        if params_serializer.validated_data["wait"]:
            cid = params_serializer.validated_data["cid"]
            filecoin_client = FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
            try:
                filecoin_client.wait_message(cid)
            except Exception as exc:
                logger.debug(f"wait message error, cid: {cid} exc: {exc}")
        return Response(data)

    @action(methods=["post"], detail=False, url_path="build-change-beneficiary-in")
    def c_build_change_beneficiary_in(self, request, *args, **kwargs):
        params_serializer = l_serializers.BuildChangeBeneficiaryIn(data=request.data)
        params_serializer.is_valid(raise_exception=True)
        filecoin_client = FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
        miner_id = params_serializer.validated_data['miner_id']
        miner_id_str = f"{settings.ADDRESS_PREFIX}0{miner_id}"
        to_address = params_serializer.validated_data["to_address"]
        to_address = settings.SPEX_LOAN_CONTRACT_T0_ADDRESS if to_address is None else to_address
        try:
            miner_info = filecoin_client.get_miner_info(miner_id=miner_id)
        except Exception as exc:
            logger.debug(f"get miner {miner_id} info error: {exc}")
            raise exceptions.ParseError(f"get miner info error: {exc}")
        keytool = Keytool(settings.KEY_TOOL_PATH)
        try:
            msg_cid_hex, msg_cid_str, msg_hex, msg_detail = keytool.build_change_beneficiary_message(
                miner_info["Beneficiary"],
                miner_id_str,
                f"{to_address}",
                "99999999999999999999999999999999999999999999999999000000000000000000",
                9223372036854775807)
        except Exception as exc:
            logger.debug(f"Build change beneficiary message error: miner_id: {miner_id} exc: {exc}")
            raise exceptions.ParseError(f"Build message error: {exc}")
        data = {
            "msg_cid_hex": msg_cid_hex,
            "msg_cid_str": msg_cid_str,
            "msg_hex": msg_hex,
            "msg_detail": msg_detail,
            "miner_info": miner_info
        }
        return Response(data)

    @action(methods=["post"], detail=False, url_path="build-change-beneficiary-out")
    def c_build_change_beneficiary_out(self, request, *args, **kwargs):
        params_serializer = l_serializers.BuildChangeBeneficiaryOut(data=request.data)
        params_serializer.is_valid(raise_exception=True)
        miner_id = params_serializer.validated_data['miner_id']
        miner_id_str = f"{settings.ADDRESS_PREFIX}0{miner_id}"
        keytool = Keytool(settings.KEY_TOOL_PATH)

        args_dict = {
            "NewBeneficiary": params_serializer.validated_data["new_beneficiary"],
            "NewQuota": params_serializer.validated_data["new_quota"],
            "NewExpiration": params_serializer.validated_data["new_expiration"],
        }
        args_str = json.dumps(args_dict)
        try:
            msg_cid_hex, msg_cid_str, msg_hex, msg_detail = keytool.build_message(
                _from=params_serializer.validated_data["new_beneficiary"],
                to=miner_id_str,
                method=30,
                args=args_str
            )
        except Exception as exc:
            logger.debug(f"Build build_change_beneficiary_out error message error miner_id: {miner_id} exc: {exc}")
            raise exceptions.ParseError(f"Build message error: {exc}")
        data = {
            "msg_cid_hex": msg_cid_hex,
            "msg_cid_str": msg_cid_str,
            "msg_hex": msg_hex,
            "msg_detail": msg_detail,
        }
        return Response(data)

    # @action(methods=["post"], detail=False, url_path="push-wait")
    # def c_push_wait_message(self, request, *args, **kwargs):
    #     pass


class Comment(mixins.RetrieveModelMixin,
              mixins.ListModelMixin,
              mixins.CreateModelMixin,
              mixins.DestroyModelMixin,
              viewsets.GenericViewSet):
    queryset = l_models.Comment.objects.all()
    serializer_class = l_serializers.Comment

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
