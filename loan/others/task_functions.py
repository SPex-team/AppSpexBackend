import json
import web3
import logging
import datetime
import eth_abi

from web3 import Web3

from web3.middleware import geth_poa_middleware


from django.conf import settings
from django.db.transaction import atomic
from django.db.utils import IntegrityError


from ..others.filecoin import FilecoinClient
from .. import models as l_models
from . import filecoin as o_filecoin

DECIMALS = 1e18
RATE_BASE = 1000000
logger = logging.getLogger("loan_tasks")


def get_spex_loan_contract():
    w3 = Web3(Web3.HTTPProvider(settings.ETH_HTTP_PROVIDER))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    address = Web3.to_checksum_address(settings.ETH_LOAN_CONTRACT_ADDRESS)
    contract = w3.eth.contract(address=address, abi=json.loads(settings.ETH_LOAN_CONTRACT_ABI_STR))
    return contract


# def get_miner_balance(miner_id: str):
#     filecoin_client = FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
#     params = [
#         miner_id,
#         None
#     ]
#     ret_data = filecoin_client.request(method="Filecoin.StateGetActor", params=params)
#     balance_human = round(int(ret_data["Balance"]) / 1e18, 2)
#     return balance_human


def get_miner_balances(miner_id: str):
    filecoin_client = FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
    params = [
        miner_id,
        None
    ]
    ret_data = filecoin_client.request(method="Filecoin.StateReadState", params=params)
    total_balance_human = int(ret_data["Balance"]) / 1e18
    locked_balance_human = int(ret_data["State"]["LockedFunds"]) / 1e18
    pledge_balance_human = int(ret_data["State"]["InitialPledge"]) / 1e18
    available_balance_human = total_balance_human - locked_balance_human - pledge_balance_human
    return total_balance_human, available_balance_human, pledge_balance_human, locked_balance_human


# def get_miner_power(miner_id: str):
#     filecoin_client = FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
#     params = [
#         miner_id,
#         None
#     ]
#     ret_data = filecoin_client.request(method="Filecoin.StateMinerPower", params=params)
#     power_t = round(int(ret_data["MinerPower"]["QualityAdjPower"]) / (1024 ** 4), 2)
#     return power_t


# def get_miner_price_human(miner_id: int):
#     price_human = 0
#     try:
#         miner_last_info = l_models.MinerLastInfo.objects.get(miner_id=miner_id)
#         price_human = miner_last_info.price_human
#     except l_models.MinerLastInfo.DoesNotExist:
#         pass
#     return price_human


# def get_miner_seller(miner_id: int):
#     seller = web3.constants.ADDRESS_ZERO
#     try:
#         miner_last_info = l_models.MinerLastInfo.objects.get(miner_id=miner_id).price_human
#         seller = miner_last_info.owner
#     except l_models.MinerLastInfo.DoesNotExist:
#         pass
#     return seller


# @atomic
def process_new_miner_log(log, tag):
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

    # l_models.Tag.objects.filter(key="last_sync_new_wallet_repayment_number").update(value=block_number)
    tag.value = str(block_number)
    tag.save()


# @atomic
def process_repayment_log(log, tag, _type):
    code = log["data"][2:]
    encoded_code = bytes.fromhex(code)
    operator_user_address, user_address, miner_id, amount = eth_abi.decode(["address", "address", "uint64", "uint256"],
                                                                           encoded_code)
    logger.info(
        f"get a new repayment log operator_user_address: {operator_user_address} miner_id: {miner_id} user_address: {user_address} amount: {amount}")
    operator_user_address = operator_user_address.lower()
    user_address = user_address.lower()

    filecoin_client = o_filecoin.FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)

    block = filecoin_client.request(method="eth_getBlockByNumber", params=[log["blockNumber"], True])
    log_timestamp = int(block["timestamp"][2:], 16)
    log_datetime = datetime.datetime.fromtimestamp(log_timestamp, tz=datetime.timezone.utc)

    # miner = l_models.Miner.objects.get(miner_id=miner_id)

    # operator_type = "wallet_repayment" if log["topics"][0] == settings.SPEX_LOAN_WALLET_PAYMENT_TOPIC else "withdraw_repayment"
    l_models.LoanOperatorRecord.objects.create(
        miner_id=miner_id,
        user_address=user_address,
        operator_user_address=operator_user_address,
        operator_type=_type,
        amount_raw=amount,
        amount_human=amount / 1e18,
        time=log_datetime
    )
    # loan_item_qs = l_models.LoanItem.objects.filter(miner_id=miner_id, user_address=user_address).order_by("-time")

    block_number = int(log["blockNumber"], 16)
    tag.value = str(block_number)
    tag.save()


def update_miner(miner: l_models.Miner):
    spex_contract = get_spex_loan_contract()
    miner_chain_info = spex_contract.functions._miners(miner.miner_id).call()
    owner = miner_chain_info[1].lower()

    # transfer_out_delegator = spex_contract.functions._releasedMinerDelegators(miner.miner_id).call()
    # transfer_out_delegator = transfer_out_delegator.lower()

    now = datetime.datetime.now()
    interval_time = now.timestamp() - miner.create_time.timestamp()

    if owner == "0x0000000000000000000000000000000000000000" and interval_time > 600:

        # if transfer_out_delegator == "0x0000000000000000000000000000000000000000":
        #     logger.info(f"the miner not in delegator and transfer_out_delegator, delete miner {miner.miner_id}")
        #     miner.delete()
        #     return

        filecoin_client = o_filecoin.FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
        miner_info = filecoin_client.get_miner_info(miner.miner_id)
        if miner_info["Beneficiary"][1:] != settings.SPEX_LOAN_CONTRACT_T0_ADDRESS[1:]:
            logger.info(f"the miner has been transferred out, delete miner {miner.miner_id}")
            miner.delete()
        else:
            miner.is_submitted_transfer_out = True
            miner.save()
        return


    current_total_debt, current_total_principal = spex_contract.functions.getCurrentTotalDebtAmount(miner.miner_id).call()

    annual_interest_rate_human = miner_chain_info[3] / RATE_BASE * 100

    miner.delegator_address = owner
    # list_miner_info = spex_contract.functions.getListMinerById(miner.miner_id).call()
    miner.max_debt_amount_raw = miner_chain_info[2]
    miner.max_debt_amount_human = miner_chain_info[2] / DECIMALS
    miner.receive_address = miner_chain_info[4].lower()
    miner.annual_interest_rate_human = annual_interest_rate_human
    miner.last_debt_amount_raw = miner_chain_info[7]
    miner.last_debt_amount_human = miner_chain_info[7] / DECIMALS
    miner.last_update_timestamp = miner_chain_info[8]
    miner.disabled = miner_chain_info[5]

    miner.current_total_debt_human = current_total_debt / DECIMALS
    miner.current_total_principal_human = current_total_principal / DECIMALS
    miner.current_total_interest_human = (current_total_debt - current_total_principal) / DECIMALS

    if miner.disabled is True and miner_chain_info[5] is False:
        miner.last_list_time = datetime.datetime.now()

    try:
        total_balance_human, available_balance_human, pledge_balance_human, locked_balance_human = get_miner_balances(f"{settings.ADDRESS_PREFIX}0{miner.miner_id}")
        miner.total_balance_human = total_balance_human
        miner.available_balance_human = available_balance_human
        miner.initial_pledge_human = pledge_balance_human
        miner.locked_rewards_human = locked_balance_human

        miner.collateral_rate = current_total_debt / DECIMALS / total_balance_human * 100

        l_models.Loan.objects.filter(miner_id=miner.miner_id).update(
            miner_total_balance_human=total_balance_human,
            annual_interest_rate=annual_interest_rate_human
        )

        # miner = l_models.Miner.objects.get(miner_id=loan.miner_id)

        # loan.miner_total_balance_human = miner.total_balance_human
        # loan.annual_interest_rate_human = miner.annual_interest_rate_human

    except Exception as exc:
        logger.warning(f"get total balance error: {exc}")
    # o_objects.MinerLastInfo.update_from_miner(miner)

    miner.completed = miner.current_total_debt_human > miner.max_debt_amount_human

    miner.save()


# @atomic
def process_new_loan_log(log, tag):
    filecoin_client = o_filecoin.FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
    code = log["data"][2:]
    encoded_code = bytes.fromhex(code)
    buyer, miner_id, amount = eth_abi.decode(["address", "uint64", "uint256"], encoded_code)
    logger.info(f"get a new loan miner_id: {miner_id} buyer: {buyer} amount: {amount}")
    buyer = buyer.lower()
    # price_human = l_task_functions.get_miner_price_human(miner_id)

    block = filecoin_client.request(method="eth_getBlockByNumber", params=[log["blockNumber"], True])
    log_timestamp = int(block["timestamp"][2:], 16)
    log_datetime = datetime.datetime.fromtimestamp(log_timestamp, tz=datetime.timezone.utc)

    miner = l_models.Miner.objects.get(miner_id=miner_id)

    l_models.LoanOperatorRecord.objects.create(
        miner_id=miner_id,
        user_address=buyer,
        operator_user_address=log["address"],
        operator_type="lend",
        amount_raw=amount,
        amount_human=amount / 1e18,
        time=log_datetime
    )

    # l_models.LoanItem.objects.get_or_create(
    #     miner_id=miner_id,
    #     user_address=buyer,
    #     annual_interest_rate=miner.annual_interest_rate_human,
    #     amount_human=amount / 1e18,
    #     time=log_datetime
    # )

    loan, is_new = l_models.Loan.objects.get_or_create(miner_id=miner_id, user_address=buyer)
    if is_new is False:
        # loan.current_total_amount_raw = str(int(loan.current_total_amount_raw) + amount)
        # loan.current_principal_human += amount / 1e18
        # loan.last_update_timestamp = log_timestamp
        # loan.save()
        return
    loan.transaction_hash = log["transactionHash"]
    loan.user_address = buyer
    loan.miner_id = miner_id
    loan.last_amount_raw = amount
    loan.last_amount_human = amount / 1e18
    loan.current_principal_human = amount / 1e18
    loan.last_update_timestamp = log_timestamp

    loan.miner_total_balance_human = miner.total_balance_human
    loan.annual_interest_rate = miner.annual_interest_rate_human

    loan.save()

    block_number = int(log["blockNumber"], 16)
    tag.value = str(block_number)
    tag.save()


def update_loan(loan: l_models.Loan):
    spex_contract = get_spex_loan_contract()
    user_address_checksum = Web3.to_checksum_address(loan.user_address)
    loan_on_chain_info = spex_contract.functions._loans(user_address_checksum, loan.miner_id).call()
    last_amount = loan_on_chain_info[0]
    now = datetime.datetime.now()
    interval_time = now.timestamp() - loan.create_time.timestamp()

    current_principal_interest, current_total_principal = spex_contract.functions.getCurrentAmountOwedToLender(user_address_checksum, loan.miner_id).call()
    # logger.debug(f"loan.id: {loan.id} current_principal_interest: {current_principal_interest} current_total_principal: {current_total_principal}")

    # if last_amount == 0 and interval_time > 600:
    #     loan.completed = True
    #     loan.save()
    #     # logger.info(
    #     #     f"the loan is not in chain, delete the loan loan.user_address: {loan.user_address} loan.miner_id: {loan.miner_id}")
    #     # loan.delete()
    #     return

    loan.last_amount_raw = loan_on_chain_info[1]
    loan.last_amount_human = loan_on_chain_info[1] / 1e18
    loan.last_update_timestamp = loan_on_chain_info[2]

    loan.completed = True if last_amount == 0 and interval_time > 600 else False
    loan.current_principal_human = current_total_principal / DECIMALS
    loan.current_interest_human = (current_principal_interest - current_total_principal) / 1e18
    loan.current_total_amount_human = current_principal_interest / DECIMALS

    loan.save()



def sync_new_repayment(_type, topic):
    tag_key = ""
    if _type == "withdraw_repayment":
        tag_key = "last_sync_new_withdraw_repayment_number"
    elif _type == "wallet_repayment":
        tag_key = "last_sync_new_wallet_repayment_number"
    else:
        raise Exception(f"unknown _type: {_type}")
    # logger.info("start sync_new_withdraw_repayment task")
    # last_sync_order_block_number_key = "last_sync_new_withdraw_repayment_number"
    last_sync_order_block_number = settings.ETH_INIT_SYNC_LOAN_HEIGHT - 1
    tag = None
    try:
        tag = l_models.Tag.objects.get(key=tag_key)
        last_sync_order_block_number = int(tag.value)
    except l_models.Tag.DoesNotExist:
        tag = l_models.Tag.objects.create(key=tag_key, value=str(last_sync_order_block_number))

    filecoin_client = o_filecoin.FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
    from_block = last_sync_order_block_number + 1
    to_block = filecoin_client.get_latest_block_number()
    if to_block-from_block >= 2880:
        to_block = from_block + 2879

    logger.info(f"from_block: {from_block} to_block: {to_block}")
    log_list = filecoin_client.get_logs(from_block, to_block, settings.ETH_LOAN_CONTRACT_ADDRESS,
                                        topics=[topic])
    for log in log_list:
        process_repayment_log(log, tag, _type)

    tag.value = str(to_block)
    tag.save()
