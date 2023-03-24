import json
import requests


class FilecoinClient:

    def __init__(self, base_url: str):
        self.base_url = base_url

    def request(self, method: str, params: list, timeout=30):
        data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(self.base_url, data=json.dumps(data), headers=headers, timeout=timeout)
        if response.status_code != 200:
            raise Exception(f"request {self.base_url} error, status_code: {response.status_code} body: {response.text}")
        response_json = response.json()
        if "error" in response_json.keys():
            raise Exception(f"request error: {response.text}")
        return response_json["result"]

    def get_miner_info(self, miner_id: int):
        params = [
            f"t0{miner_id}", None
        ]
        return self.request(method="Filecoin.StateMinerInfo", params=params)

    def wait_message(self, cid: str):
        params = [{"/": cid}, 3, 100, False]
        return self.request(method="Filecoin.StateWaitMsg", params=params, timeout=60)
