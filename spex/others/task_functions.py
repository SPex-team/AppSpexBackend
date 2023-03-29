from django.conf import settings

from ..others.filecoin import FilecoinClient


def get_miner_balance(miner_id: str):
    filecoin_client = FilecoinClient(settings.ETH_HTTP_PROVIDER)
    params = [
        miner_id,
        None
    ]
    ret_data = filecoin_client.request(method="Filecoin.StateGetActor", params=params)
    balance_human = round(ret_data["Balance"] / 1e18, 2)
    return balance_human

