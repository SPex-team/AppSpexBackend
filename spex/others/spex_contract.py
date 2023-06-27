import json

from web3 import Web3

from .filecoin import FilecoinClient


class SpexContract:

    def __init__(self, filecoin_client: FilecoinClient, contract_address: str):
        self.filecoin_client = filecoin_client
        self.contract_address = contract_address
        # w3 = Web3(Web3.HTTPProvider(http_provider))
        # self.contract = w3.eth.contract(address=address, abi=json.loads(abi_str))

    # def get_events(self, name: str):
    #     event_filter = self.contract.events.ValidatorRegistration.createFilter(fromBlock=7287273, toBlock=7287273 + 1000)
    #     event_list = event_filter.get_all_entries()
    #     return event_list

    def get_event_miner_in_contract(self, from_block: int, to_block: int | None):

        params = {
            "fromBlock": hex(from_block),
            "address": self.contract_address
        }
        if to_block is not None:
            params["toBlock"] = hex(to_block)

        result = self.filecoin_client.request("eth_getLogs", params)






