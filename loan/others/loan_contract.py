import json

from web3 import Web3

from .filecoin import FilecoinClient


class LoanContract:

    def __init__(self, filecoin_client: FilecoinClient, contract_address: str):
        self.filecoin_client = filecoin_client
        self.contract_address = contract_address


    def get_event_miner_in_contract(self, from_block: int, to_block):

        params = {
            "fromBlock": hex(from_block),
            "address": self.contract_address
        }
        if to_block is not None:
            params["toBlock"] = hex(to_block)

        result = self.filecoin_client.request("eth_getLogs", params)






