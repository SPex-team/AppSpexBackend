import time
import hmac
import json
import logging
from base64 import standard_b64encode

import requests

from devops_django import tools as dd_tools

logger = logging.getLogger("dingtalk")


class NotFoundError(Exception):
    pass


class Dingtalk:
    code_exception_map = {
        404: NotFoundError
    }

    def __init__(self, app_key=None, app_secret=None):
        self.origin = "https://oapi.dingtalk.com"
        self.headers = {
            "Content-Type": "application/json",
        }
        self.timeout = 10
        self.app_key = app_key
        self.app_secret = app_secret

    def request(self, url, method="get", data={}, params={}):
        url = self.origin + url
        logger.debug(f"method: {method} url: {url} params: {params} data: {data}")
        try:
            response = getattr(requests, method)(url, data=json.dumps(data), headers=self.headers, params=params,
                                                 timeout=self.timeout)
            if response.status_code in self.code_exception_map:
                raise self.code_exception_map[response.status_code](response.text)
            logger.debug(response.text)
            res_data = response.json()
        except Exception as exc:
            logger.error(f"request Dingtalk exception: {exc}")
            raise exc
        if "errcode" in res_data and res_data["errcode"] != 0:
            raise Exception(response.text)
        return res_data

    @dd_tools.InstanceMethodCache(time=7000)
    def get_access_token(self):
        if self.app_key is None or self.app_secret is None:
            raise Exception("app_key or app_secret is None")
        url = f"/gettoken?appkey={self.app_key}&appsecret={self.app_secret}"
        return self.request(url)["access_token"]

    @classmethod
    def signature(cls, secret, timestamp):
        str_timestamp = str(timestamp)
        digest = hmac.HMAC(key=secret.encode('utf8'), msg=str_timestamp.encode('utf8'),
                           digestmod=hmac._hashlib.sha256).digest()
        signature = standard_b64encode(digest).decode('utf8')
        return signature


class GroupRobot:
    """
    Robo
    """

    headers = {
        "Content-Type": "application/json"
    }

    def __init__(self, robot_url):
        self.robot_url = robot_url

    def send_message(self, message, at_list=[]):
        data = {
            "msgtype": "text",
            "text": {
                "content": message
            },
            "at": {
                "atMobiles": at_list
            },
        }
        logger.debug(f"url: {self.robot_url} message: {message}")
        try:
            response = requests.post(self.robot_url, headers=self.headers, data=json.dumps(data), timeout=10)
            logger.debug(response.text)
            res_data = response.json()
        except Exception as exc:
            logger.error(f"请求钉钉发生异常 {exc}")
            raise exc
        if res_data["errcode"] != 0:
            raise Exception(res_data["errmsg"])


if __name__ == '__msain__':
    from urllib.parse import quote_plus

    dingtalk = Dingtalk()

    appid = "dingoa4f6itn1g5wdfvysn"
    secret = "_x9Q0r5CVqVA36ZIG24t0hLFY3okrITZ7LCG9ZvIi5DNVn5lG-uHLSd-CpnfWKjG"
    timestamp = time.time()
    timestamp = round(timestamp * 1000)
    signature = Dingtalk.signature(secret, timestamp)

    # signature = get_signature(secret, timestamp)
    signature_encoded = quote_plus(signature)
    # url = f"https://oapi.dingtalk.com/sns/getuserinfo_bycode?accessKey={appid}&timestamp={timestamp}&signature={signature_encoded}"
    url = f"https://oapi.dingtalk.com/sns/getuserinfo_bycode"
    data = {
        "tmp_auth_code": "4924cacf58a83e22864a0a7f3e122b8f"
    }
    # response = requests.post(url, data=json.dumps(data))
    # print(response.text)
    params = {
        "accessKey": appid,
        "timestamp": timestamp,
        "signature": signature
    }
    response = requests.post(url, data=json.dumps(data), params=params)
    print(response.text)
    res_data = dingtalk.request("/sns/getuserinfo_bycode", "post", data=data, params=params)
    # res_data = dingtalk.request(url, "post", data=data)
    print(res_data)

if __name__ == '__main__':
    # app_key = "dingctwi95ykubi73uic"
    # app_secret = "j5XUIusrUiDpqZTxvYUnvMYyXr8AwaSVzvpsoybDBd31R0eWbWr5DxQKgMkNXNb0"
    # dingtalk = Dingtalk(app_key, app_secret)
    # access_token = dingtalk.get_access_token()
    # url = "/user/listbypage"
    # params = {
    #     "access_token": access_token,
    #     "department_id": 1,
    #     "offset": 1,
    #     "size": 1
    # }
    # res_data = dingtalk.request(url, params=params)
    # res_data = json.dumps(res_data, indent="\t")
    # print(res_data)

    group_robot = GroupRobot(
        robot_url="https://oapi.dingtalk.com/robot/send?access_token=53ab2b3ef09b4f1ad9bc88b8db3e13a1c132ebeaf0eccd7a90c55d66426f5ccd")
    group_robot.send_message("lalala")
