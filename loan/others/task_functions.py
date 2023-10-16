
import web3

from django.conf import settings

from ..others.filecoin import FilecoinClient
from .. import models as l_models


def get_miner_balance(miner_id: str):
    filecoin_client = FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
    params = [
        miner_id,
        None
    ]
    ret_data = filecoin_client.request(method="Filecoin.StateGetActor", params=params)
    balance_human = round(int(ret_data["Balance"]) / 1e18, 2)
    return balance_human


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


def get_miner_power(miner_id: str):
    filecoin_client = FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
    params = [
        miner_id,
        None
    ]
    ret_data = filecoin_client.request(method="Filecoin.StateMinerPower", params=params)
    power_t = round(int(ret_data["MinerPower"]["QualityAdjPower"]) / (1024 ** 4), 2)
    return power_t


def get_miner_price_human(miner_id: int):
    price_human = 0
    try:
        miner_last_info = l_models.MinerLastInfo.objects.get(miner_id=miner_id)
        price_human = miner_last_info.price_human
    except l_models.MinerLastInfo.DoesNotExist:
        pass
    return price_human


def get_miner_seller(miner_id: int):
    seller = web3.constants.ADDRESS_ZERO
    try:
        miner_last_info = l_models.MinerLastInfo.objects.get(miner_id=miner_id).price_human
        seller = miner_last_info.owner
    except l_models.MinerLastInfo.DoesNotExist:
        pass
    return seller
