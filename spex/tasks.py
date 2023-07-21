import datetime
import json
import logging

import eth_abi
import web3.constants
import traceback

from celery import shared_task

from django.conf import settings
from django.db import transaction
from django.db.utils import IntegrityError
from django.db.transaction import atomic

from .others.spex_contract import SpexContract

from . import models as l_models
from .others import task_functions as l_task_functions
from .others import filecoin as o_filecoin


logger = logging.getLogger("tasks")


from web3 import Web3

from web3.middleware import geth_poa_middleware


def get_spex_contract():
    w3 = Web3(Web3.HTTPProvider(settings.ETH_HTTP_PROVIDER))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    address = Web3.to_checksum_address(settings.ETH_CONTRACT_ADDRESS)
    contract = w3.eth.contract(address=address, abi=json.loads(settings.ETH_CONTRACT_ABI_STR))
    return contract


# def sync_new_miners():
#     sync_height_tag, is_new = l_models.Tag.objects.get_or_create(key="MINER_SYNC_HEIGHT")
#     sync_height = int(sync_height_tag.value)
#     if is_new:
#         sync_height = settings.ETH_INIT_SYNC_HEIGHT
#     spex_contract = get_spex_contract()
#     event_filter = spex_contract.events.EventMinerInContract.createFilter(fromBlock=sync_height)
#     entries = event_filter.get_all_entries()
#     for item in entries:
#         l_models.Miner.objects.create(
#             miner_id=str(item.args["minerId"]),
#             owner=item.args["owner"]
#         )

def add_empty_miner_save_index(miner_id: int, tag: l_models.Tag, index: int):
    try:
        l_models.Miner.objects.create(
            miner_id=miner_id,
            owner="0x0000000000000000000000000000000000000000",
            is_list=False,
        )
    except IntegrityError as exc:
            logger.warning(f"Add miner {miner_id} error: {exc}")
    tag.value = str(index)
    tag.save()


@shared_task
def sync_new_miners():
    last_sync_miner_block_number_key = "last_sync_miner_block_number"
    last_sync_miner_block_number = settings.ETH_INIT_SYNC_HEIGHT - 1
    tag = None
    try:
        tag = l_models.Tag.objects.get(key=last_sync_miner_block_number_key)
        last_sync_miner_block_number = int(tag.value)
    except l_models.Tag.DoesNotExist:
        tag = l_models.Tag.objects.create(key=last_sync_miner_block_number_key, value=str(last_sync_miner_block_number))

    filecoin_client = o_filecoin.FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
    from_block = last_sync_miner_block_number + 1
    to_block = filecoin_client.get_latest_block_number()

    logger.info(f"from_block: {from_block} to_block: {to_block}")
    log_list = filecoin_client.get_logs(from_block, to_block, settings.ETH_CONTRACT_ADDRESS, topics=[settings.SPEX_MINER_IN_CONTRACT_TOPIC])
    for log in log_list:
        code = log["data"][2:]
        encoded_code = bytes.fromhex(code)
        miner_id, owner = eth_abi.decode(["uint64", "address"], encoded_code)
        logger.info(f"get a new miner miner_id: {miner_id} owner: {owner}")
        owner = owner.lower()
        try:
            l_models.Miner.objects.create(
                miner_id=miner_id,
                owner=owner,
                is_list=False,
            )
        except IntegrityError as exc:
            logger.info(f"catch IntegrityError when Add miner {miner_id} exc: {exc}")
        block_number = int(log["blockNumber"], 16)
        tag.value = str(block_number)
        tag.save()

    tag.value = str(to_block)
    tag.save()


def update_miner(miner: l_models.Miner):
    spex_contract = get_spex_contract()
    owner = spex_contract.functions.getMinerDelegator(miner.miner_id).call()
    owner = owner.lower()

    transfer_out_delegator = spex_contract.functions.getTransferOutMinerDelegator(miner.miner_id).call()
    transfer_out_delegator = transfer_out_delegator.lower()

    now = datetime.datetime.now()
    interval_time = now.timestamp() - miner.create_time.timestamp()

    if owner == "0x0000000000000000000000000000000000000000" and interval_time > 600:

        if transfer_out_delegator == "0x0000000000000000000000000000000000000000":
            logger.info(f"the miner not in delegator and transfer_out_delegator, delete miner {miner.miner_id}")
            miner.delete()
            return

        filecoin_client = o_filecoin.FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
        miner_info = filecoin_client.get_miner_info(miner.miner_id)
        if miner_info["Owner"][1:] != settings.SPEX_CONTRACT_T0_ADDRESS[1:]:
            logger.info(f"the miner has been transferred out, delete miner {miner.miner_id}")
            miner.delete()
        else:
            miner.is_submitted_transfer_out = True
            miner.save()
        return
    miner.owner = owner
    list_miner_info = spex_contract.functions.getListMinerById(miner.miner_id).call()
    miner.is_list = False if list_miner_info[0] == 0 else True
    miner.buyer = list_miner_info[2]
    miner.price = list_miner_info[3] / 1e18
    miner.price_raw = str(list_miner_info[3])
    miner.list_time = list_miner_info[4]
    try:
        miner.balance_human = l_task_functions.get_miner_balance(f"{settings.ADDRESS_PREFIX}0{miner.miner_id}")
    except Exception as exc:
        logger.warning(f"get balance error: {exc}")
    try:
        miner.power_human = l_task_functions.get_miner_power(f"{settings.ADDRESS_PREFIX}0{miner.miner_id}")
    except Exception as exc:
        logger.warning(f"get power error: {exc}")

    if miner.is_list:
        try:
            miner_price = l_models.MinerPrice.objects.get(miner_id=miner.miner_id)
            miner_price.price_human = miner.price
            miner_price.save()
        except l_models.MinerPrice.DoesNotExist:
            l_models.MinerPrice.objects.create(miner_id=miner.miner_id, price_human=miner.price)
            
    miner.save()


@shared_task
def update_all_miners():
    # sync_height_str = l_models.Tag.objects.get_or_create(key="MINER_SYNC_HEIGHT")
    # sync_height = int(sync_height_str)
    # spex_contract = SpexContract(settings.ETHE_HTTP_PROVIDER, settings.ETH_CONTRACT_ADDRESS, settings.ETH_CONTRACT_ABI_STR)

    miner_qs = l_models.Miner.objects.filter().all()
    for miner in miner_qs:
        try:
            update_miner(miner)
        except Exception as exc:
            logger.error(f"Failed sync miner {miner.miner_id}, exc: {exc}")


# @shared_task
# def listen_sync_new_miners():
#     spex_contract = get_spex_contract()
#     event_filter = spex_contract.events.EventMinerInContract.create_filter(fromBlock="latest")
#     for event in event_filter.get_new_entries():
#         pass


@shared_task
def sync_new_orders():
    last_sync_order_block_number_key = "last_sync_order_block_number"
    last_sync_order_block_number = settings.ETH_INIT_SYNC_HEIGHT - 1
    tag = None
    try:
        tag = l_models.Tag.objects.get(key=last_sync_order_block_number_key)
        last_sync_order_block_number = int(tag.value)
    except l_models.Tag.DoesNotExist:
        tag = l_models.Tag.objects.create(key=last_sync_order_block_number_key, value=str(last_sync_order_block_number))

    filecoin_client = o_filecoin.FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
    from_block = last_sync_order_block_number + 1
    to_block = filecoin_client.get_latest_block_number()

    logger.info(f"from_block: {from_block} to_block: {to_block}")
    log_list = filecoin_client.get_logs(from_block, to_block, settings.ETH_CONTRACT_ADDRESS, topics=[settings.SPEX_BUY_MINER_CONTRACT_TOPIC])
    for log in log_list:
        code = log["data"][2:]
        encoded_code = bytes.fromhex(code)
        miner_id, buyer, price = eth_abi.decode(["uint64", "address", "uint256"], encoded_code)
        logger.info(f"get a new miner miner_id: {miner_id} buyer: {buyer} price: {price}")
        buyer = buyer.lower()
        price_human = l_task_functions.get_miner_price_human(miner_id)
        try:
            order = l_models.Order.objects.create(
                transaction_hash=log["transactionHash"],
                miner_id=miner_id,
                seller=web3.constants.ADDRESS_ZERO,
                buyer=buyer,
                price_human=price_human,
            )
        except IntegrityError as exc:
            logger.info(f"catch IntegrityError when Add miner {miner_id} exc: {exc}")
        else:
            try:
                order.balance_human = l_task_functions.get_miner_balance(f"{settings.ADDRESS_PREFIX}0{miner_id}")
            except Exception as exc:
                logger.warning(f"get balance error: {exc}")
            try:
                order.power_human = l_task_functions.get_miner_power(f"{settings.ADDRESS_PREFIX}0{miner_id}")
            except Exception as exc:
                logger.warning(f"get power error: {exc}")
            time = datetime.datetime.now()
            try:
                timestamp_hex = filecoin_client.request(method="eth_getBlockByNumber", params=[log["blockNumber"]])
                timestamp = int(timestamp_hex, 16)
                time = datetime.datetime.fromtimestamp(timestamp)
            except Exception as exc:
                logger.warning(f"get block timestamp error: {exc}")
            order.time = time
            order.save()

        block_number = int(log["blockNumber"], 16)
        tag.value = str(block_number)
        tag.save()

    tag.value = str(to_block)
    tag.save()
