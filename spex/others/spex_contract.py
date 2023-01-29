import json

from web3 import Web3


class SpexContract:

    def __init__(self, http_provider: str, address: str, abi_str: str):
        w3 = Web3(Web3.HTTPProvider(http_provider))
        self.contract = w3.eth.contract(address=address, abi=json.loads(abi_str))

    def get_events(self, name: str):
        event_filter = self.contract.events.ValidatorRegistration.createFilter(fromBlock=7287273, toBlock=7287273 + 1000)
        event_list = event_filter.get_all_entries()
        return event_list





