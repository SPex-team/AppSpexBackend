import json
import requests
from django.conf import settings


class FilecoinClient:

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token

    def request(self, method: str, params: list, timeout=30):
        data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        headers = {
            "Content-Type": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        response = requests.post(self.base_url, data=json.dumps(data), headers=headers, timeout=timeout)
        if response.status_code != 200:
            raise Exception(f"request {self.base_url} error, status_code: {response.status_code} body: {response.text}")
        response_json = response.json()
        if "error" in response_json.keys():
            raise Exception(f"request error: {response.text}")
        return response_json["result"]

    def get_miner_info(self, miner_id: int):
        params = [
            f"{settings.ADDRESS_PREFIX}0{miner_id}", None
        ]
        return self.request(method="Filecoin.StateMinerInfo", params=params)

    def wait_message(self, cid: str):
        params = [{"/": cid}, 3, 100, False]
        return self.request(method="Filecoin.StateWaitMsg", params=params, timeout=60)

    def get_latest_block_number(self):
        result = self.request(method="eth_blockNumber", params=[], timeout=60)
        return int(result, 16)

    def get_logs(self, from_block, to_block, contract_address, topics):
        args = {
            "fromBlock": hex(from_block)
        }
        if to_block:
            args["toBlock"] = hex(to_block)
        if contract_address:
            args["address"] = [contract_address]
        if topics:
            args["topics"] = topics
        return self.request(method="eth_getLogs", params=[args], timeout=60)

    # def get_miner_info(self, miner_id):
    #     result = self.request(method="Filecoin.StateMinerInfo", params=[miner_id, None], timeout=60)
    #     return result

