import datetime
import json
import time
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
from web3 import Web3

from . import models as l_models
from .others import task_functions as l_task_functions
from .others import filecoin as o_filecoin
from .others import objects as o_objects

logger = logging.getLogger("loan_tasks")


@shared_task
def sync_new_miners():
    logger.info("start sync_new_miners task")
    last_sync_miner_block_number_key = "last_sync_miner_block_number"
    last_sync_miner_block_number = settings.ETH_INIT_SYNC_LOAN_HEIGHT - 1
    tag = None
    try:
        tag = l_models.Tag.objects.get(key=last_sync_miner_block_number_key)
        last_sync_miner_block_number = int(tag.value)
    except l_models.Tag.DoesNotExist:
        tag = l_models.Tag.objects.create(key=last_sync_miner_block_number_key, value=str(last_sync_miner_block_number))

    filecoin_client = o_filecoin.FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
    from_block = last_sync_miner_block_number + 1
    to_block = filecoin_client.get_latest_block_number()
    if to_block-from_block >= 2880:
        to_block = from_block + 2879

    logger.info(f"from_block: {from_block} to_block: {to_block}")
    log_list = filecoin_client.get_logs(from_block, to_block, settings.ETH_LOAN_CONTRACT_ADDRESS,
                                        topics=[settings.SPEX_LOAN_MINER_IN_CONTRACT_TOPIC])
    for log in log_list:
        l_task_functions.process_new_miner_log(log, tag)

    tag.value = str(to_block)
    tag.save()


@shared_task
def update_all_miners():
    logger.info("start update_all_miners task")
    miner_qs = l_models.Miner.objects.filter().all()
    for miner in miner_qs:
        try:
            l_task_functions.update_miner(miner)
        except Exception as exc:
            logger.error(f"Failed sync miner {miner.miner_id}, exc: {exc}")


@shared_task
def sync_new_loans():
    logger.info("start sync_new_loans task")
    last_sync_order_block_number_key = "last_sync_new_loans_number"
    last_sync_order_block_number = settings.ETH_INIT_SYNC_LOAN_HEIGHT - 1
    tag = None
    try:
        tag = l_models.Tag.objects.get(key=last_sync_order_block_number_key)
        last_sync_order_block_number = int(tag.value)
    except l_models.Tag.DoesNotExist:
        tag = l_models.Tag.objects.create(key=last_sync_order_block_number_key, value=str(last_sync_order_block_number))

    filecoin_client = o_filecoin.FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
    from_block = last_sync_order_block_number + 1
    to_block = filecoin_client.get_latest_block_number()
    if to_block - from_block >= 2880:
        to_block = from_block + 2879

    if from_block >= to_block:
        return

    logger.info(f"from_block: {from_block} to_block: {to_block}")
    log_list = filecoin_client.get_logs(from_block, to_block, settings.ETH_LOAN_CONTRACT_ADDRESS,
                                        topics=[settings.SPEX_LOAN_LEND_TO_MINER_TOPIC])
    for log in log_list:
        l_task_functions.process_new_loan_log(log, tag)

    tag.value = str(to_block)
    tag.save()


@shared_task
def update_all_loans():
    logger.info("start update_all_loans task")
    loan_qs = l_models.Loan.objects.filter().all()
    for loan in loan_qs:
        try:
            l_task_functions.update_loan(loan)
        except Exception as exc:
            logger.error(
                f"Failed sync loan loan.user_address: {loan.user_address} loan.miner_id: {loan.miner_id}, exc: {exc}")


@shared_task
def sync_new_withdraw_repayment():
    logger.info("start sync_new_withdraw_repayment task")
    l_task_functions.sync_new_repayment(_type="withdraw_repayment", topic=settings.SPEX_LOAN_WITHDRAW_PAYMENT_TOPIC)


@shared_task
def sync_new_wallet_repayment():
    logger.info("start sync_new_wallet_repayment task")
    l_task_functions.sync_new_repayment(_type="wallet_repayment", topic=settings.SPEX_LOAN_WALLET_PAYMENT_TOPIC)


