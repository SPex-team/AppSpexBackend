
from django.conf import settings


from .others.spex_contract import SpexContract


def sync_miners():
    spex_contract = SpexContract(settings.ETHEREUM_HTTP_PROVIDER, settings.CONTRACT_ADDRESS, settings.CONTRACT_ABI_STR)
    spex_contract.get_events("")
