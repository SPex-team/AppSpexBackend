import json
import logging

from django.conf import settings
from django.db import transaction
from .others.spex_contract import SpexContract

from . import models as l_models


logger = logging.getLogger("tasks")


from web3 import Web3

from web3.middleware import geth_poa_middleware


def get_spex_contract():
    w3 = Web3(Web3.HTTPProvider(settings.ETH_HTTP_PROVIDER))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    address = Web3.toChecksumAddress(settings.ETH_CONTRACT_ADDRESS)
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

def sync_new_miners():
    pass


def sync_miner(miner: l_models.Miner):
    spex_contract = get_spex_contract()
    owner = spex_contract.functions.getOwnerById(miner.miner_id).call()
    if owner == "0x0000000000000000000000000000000000000000":
        miner.delete()
        return
    miner.owner = owner
    list_miner_info = spex_contract.functions.getListMinerById(miner.miner_id).call()
    miner.is_list = False if list_miner_info[0] == 0 else True
    miner.price = list_miner_info[2] / 1e18
    miner.list_time = list_miner_info[3]
    miner.save()


def sync_miners():
    # sync_height_str = l_models.Tag.objects.get_or_create(key="MINER_SYNC_HEIGHT")
    # sync_height = int(sync_height_str)
    spex_contract = SpexContract(settings.ETHE_HTTP_PROVIDER, settings.ETH_CONTRACT_ADDRESS, settings.ETH_CONTRACT_ABI_STR)

    miner_qs = l_models.Miner.objects.all()
    for miner in miner_qs:
        try:
            sync_miner(miner)
        except Exception as exc:
            logger.error(f"Failed sync miner {miner.id}, exc: {exc}")
