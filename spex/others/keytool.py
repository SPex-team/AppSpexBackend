import re
import time
import json
import copy
import random
import logging
import datetime
import subprocess

from django.conf import settings

logger = logging.getLogger(__name__)


class Keytool:

    def __init__(self, project_path):
        self.project_path = project_path

    def run_cmd(self, cmd, timeout=20):
        cmd = f"cd {self.project_path};{cmd}"
        logger.info(f"run cmd: {cmd}")

        if settings.ENV == "LOCAL":
            random_number = random.random()
            sleep_second = random_number * 0.1
            time.sleep(sleep_second)
        start_time = datetime.datetime.now()
        try:
            cp = subprocess.run(cmd, shell=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"timeout ({timeout}s)")
        end_time = datetime.datetime.now()
        time_cost = (end_time - start_time).total_seconds()
        logger.info(
            f"cmd run completed  time_cost: {time_cost} cmd: {cmd} returncode: {cp.returncode} stdout: {cp.stdout}, stderr: {cp.stderr}")
        if cp.returncode != 0:
            err_msg = f"run cmd: {cmd} failed, stdout: {cp.stdout} stderr: {cp.stderr}"
            raise Exception(err_msg)
        return cp.stdout

    def build_message(self, _from: str, to: str, args: str):
        cmd = f"./keytool message build --from {_from} -t {to} --method 23 --args='{args}'"
        stdout = self.run_cmd(cmd)
        msg_cid_hex = stdout.split("msgCidHex__")[1].split("__msgCidHex")[0]
        msg_cid_str = stdout.split("msgCidStr__")[1].split("__msgCidStr")[0]
        msg_hex = stdout.split("msgHex__")[1].split("__msgHex")[0]
        msg_detail = stdout.split("|detail:")[1].split("|build message success")[0]
        return msg_cid_hex, msg_cid_str, msg_hex, msg_detail

    def push_message_spex(self, message: str, sign: str):
        cmd = f"./keytool message push_spex --message {message} --sign {sign}"
        stdout = self.run_cmd(cmd)
        result = re.search(r'push message\(\w{62}\) success', stdout)
        if result is None:
            raise Exception(f"Failed push: {stdout}")
        return stdout
