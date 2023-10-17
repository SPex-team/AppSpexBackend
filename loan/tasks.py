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
from web3.middleware import geth_poa_middleware

from . import models as l_models
from .others import task_functions as l_task_functions
from .others import filecoin as o_filecoin
from .others import objects as o_objects

logger = logging.getLogger("loan_tasks")

DECIMALS = 1e18
RATE_BASE = 1000000


def get_spex_loan_contract():
    w3 = Web3(Web3.HTTPProvider(settings.ETH_HTTP_PROVIDER))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    address = Web3.to_checksum_address(settings.ETH_LOAN_CONTRACT_ADDRESS)
    contract = w3.eth.contract(address=address, abi=json.loads(settings.ETH_LOAN_CONTRACT_ABI_STR))
    return contract


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

    logger.info(f"from_block: {from_block} to_block: {to_block}")
    log_list = filecoin_client.get_logs(from_block, to_block, settings.ETH_LOAN_CONTRACT_ADDRESS,
                                        topics=[settings.SPEX_LOAN_MINER_IN_CONTRACT_TOPIC])
    for log in log_list:
        code = log["data"][2:]
        encoded_code = bytes.fromhex(code)
        miner_id, delegator_address, max_debt_amount_raw, annual_interest_rate_raw, receive_address = eth_abi.decode(
            ["uint64", "address", "uint", "uint", "address"], encoded_code)
        logger.info(
            f"get a new miner miner_id: {miner_id} owner: {delegator_address} max_debt_amount_raw: {max_debt_amount_raw} annual_interest_rate_raw: {annual_interest_rate_raw}")
        delegator_address = delegator_address.lower()
        receive_address = receive_address.lower()
        try:
            l_models.Miner.objects.create(
                miner_id=miner_id,
                delegator_address=delegator_address,
                max_debt_amount_raw=max_debt_amount_raw,
                max_debt_amount_human=max_debt_amount_raw / DECIMALS,
                annual_interest_rate_human=annual_interest_rate_raw / RATE_BASE,
                receive_address=receive_address,
            )
        except IntegrityError as exc:
            logger.info(f"catch IntegrityError when Add miner {miner_id} exc: {exc}")
        block_number = int(log["blockNumber"], 16)
        tag.value = str(block_number)
        tag.save()

    tag.value = str(to_block)
    tag.save()


def update_miner(miner: l_models.Miner):
    spex_contract = get_spex_loan_contract()
    miner_chain_info = spex_contract.functions._miners(miner.miner_id).call()
    owner = miner_chain_info[1].lower()

    transfer_out_delegator = spex_contract.functions._releasedMinerDelegators(miner.miner_id).call()
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
        if miner_info["Beneficiary"][1:] != settings.SPEX_LOAN_CONTRACT_T0_ADDRESS[1:]:
            logger.info(f"the miner has been transferred out, delete miner {miner.miner_id}")
            miner.delete()
        else:
            miner.is_submitted_transfer_out = True
            miner.save()
        return

    miner.delegator_address = owner
    # list_miner_info = spex_contract.functions.getListMinerById(miner.miner_id).call()
    miner.max_debt_amount_raw = miner_chain_info[2]
    miner.max_debt_amount_human = miner_chain_info[2] / DECIMALS
    miner.receive_address = miner_chain_info[4].lower()
    miner.annual_interest_rate_human = miner_chain_info[3] / RATE_BASE * 100
    miner.last_debt_amount_raw = miner_chain_info[6]
    miner.last_debt_amount_human = miner_chain_info[6] / DECIMALS
    miner.last_update_timestamp = miner_chain_info[7]
    miner.disabled = miner_chain_info[5]

    try:
        total_balance_human, available_balance_human, pledge_balance_human, locked_balance_human = l_task_functions. \
            get_miner_balances(f"{settings.ADDRESS_PREFIX}0{miner.miner_id}")
        miner.total_balance_human = total_balance_human
        miner.available_balance_human = available_balance_human
        miner.initial_pledge_human = pledge_balance_human
        miner.locked_rewards_human = locked_balance_human
    except Exception as exc:
        logger.warning(f"get total balance error: {exc}")
    # o_objects.MinerLastInfo.update_from_miner(miner)
    miner.save()


@shared_task
def update_all_miners():
    logger.info("start update_all_miners task")
    miner_qs = l_models.Miner.objects.filter().all()
    for miner in miner_qs:
        try:
            update_miner(miner)
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

    logger.info(f"from_block: {from_block} to_block: {to_block}")
    log_list = filecoin_client.get_logs(from_block, to_block, settings.ETH_LOAN_CONTRACT_ADDRESS,
                                        topics=[settings.SPEX_LOAN_BUY_BUY_DEBT_TOPIC])
    for log in log_list:
        code = log["data"][2:]
        encoded_code = bytes.fromhex(code)
        buyer, miner_id, amount = eth_abi.decode(["address", "uint64", "uint256"], encoded_code)
        logger.info(f"get a new loan miner_id: {miner_id} buyer: {buyer} amount: {amount}")
        buyer = buyer.lower()
        # price_human = l_task_functions.get_miner_price_human(miner_id)

        loan, is_new = l_models.Loan.objects.get_or_create(miner_id=miner_id, user_address=buyer)
        if is_new is False:
            continue
        loan.transaction_hash = log["transactionHash"],
        loan.user_address = buyer,
        loan.miner_id = miner_id,
        loan.last_amount_raw = amount,
        loan.last_amount_human = amount / 1e18,
        loan.current_principal_human = amount / 1e18,
        loan.last_update_timestamp = int(time.time())

        miner = l_models.Miner.objects.get(miner_id=miner_id)

        loan.miner_total_balance_human = miner.total_balance_human
        loan.annual_interest_rate = miner.annual_interest_rate_human

        l_models.LoanItem.objects.get_or_create(
            miner_id=miner_id,
            user_address=buyer,
            annual_interest_rate=miner.annual_interest_rate_human,
            amount_human=amount / 1e18,
        )

    tag.value = str(to_block)
    tag.save()


def update_loan(loan: l_models.Loan):
    spex_contract = get_spex_loan_contract()
    user_address_checksum = Web3.to_checksum_address(loan.user_address)
    loan_on_chain_info = spex_contract.functions._loans(user_address_checksum, loan.miner_id).call()
    last_amount = loan_on_chain_info[0]
    now = datetime.datetime.now()
    interval_time = now.timestamp() - loan.create_time.timestamp()

    # if last_amount == 0 and interval_time > 600:
    #     logger.info(
    #         f"the loan is not in chain, delete the loan loan.user_address: {loan.user_address} loan.miner_id: {loan.miner_id}")
    #     loan.delete()
    #     return
    miner = l_models.Miner.objects.get(miner_id=loan.miner_id)

    loan.miner_total_balance_human = miner.total_balance_human
    loan.annual_interest_rate_human = miner.annual_interest_rate_human

    loan.last_amount_raw = loan_on_chain_info[0]
    loan.last_amount_human = loan_on_chain_info[0] / 1e18
    loan.last_update_timestamp = loan_on_chain_info[1]

    loan.save()


@shared_task
def update_all_loans():
    logger.info("start update_all_loans task")
    loan_qs = l_models.Loan.objects.filter().all()
    for loan in loan_qs:
        try:
            update_loan(loan)
        except Exception as exc:
            logger.error(
                f"Failed sync loan loan.user_address: {loan.user_address} loan.miner_id: {loan.miner_id}, exc: {exc}")
