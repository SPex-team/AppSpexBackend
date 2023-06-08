from django.conf import settings

from ..others.filecoin import FilecoinClient


def get_miner_balance(miner_id: str):
    filecoin_client = FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
    params = [
        miner_id,
        None
    ]
    ret_data = filecoin_client.request(method="Filecoin.StateGetActor", params=params)
    balance_human = round(int(ret_data["Balance"]) / 1e18, 2)
    return balance_human


def get_miner_power(miner_id: str):
    filecoin_client = FilecoinClient(settings.ETH_HTTP_PROVIDER, settings.FILECOIN_API_TOKEN)
    params = [
        miner_id,
        None
    ]
    ret_data = filecoin_client.request(method="Filecoin.StateMinerPower", params=params)
    power_t = round(int(ret_data["MinerPower"]["QualityAdjPower"]) / (1024 ** 4), 2)
    return power_t

