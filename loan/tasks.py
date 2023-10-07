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

from spex.others.spex_contract import SpexContract

from . import models as l_models
from .others import task_functions as l_task_functions
from .others import filecoin as o_filecoin
from .others import objects as o_objects


logger = logging.getLogger("loan_tasks")


DECIMALS = 1e18


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
        miner_id, delegator_address, max_debt_amount_raw, annual_interest_rate_raw = eth_abi.decode(["uint64", "address", "uint", "uint", "address"], encoded_code)
        logger.info(f"get a new miner miner_id: {miner_id} owner: {delegator_address} max_debt_amount_raw: {max_debt_amount_raw} annual_interest_rate_raw: {annual_interest_rate_raw}")
        delegator_address = delegator_address.lower()
        try:
            l_models.Miner.objects.create(
                miner_id=miner_id,
                delegator_address=delegator_address,
                max_debt_amount_raw=max_debt_amount_raw,
                max_debt_amount_human=max_debt_amount_raw/DECIMALS,
                annual_interest_rate_raw=annual_interest_rate_raw,
                annual_interest_rate_human=annual_interest_rate_raw/DECIMALS
            )
        except IntegrityError as exc:
            logger.info(f"catch IntegrityError when Add miner {miner_id} exc: {exc}")
        block_number = int(log["blockNumber"], 16)
        tag.value = str(block_number)
        tag.save()

    tag.value = str(to_block)
    tag.save()
