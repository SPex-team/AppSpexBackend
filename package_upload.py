#!/usr/bin/env python3
# coding: utf-8

import subprocess
import datetime


def run_cmd(cmd):
    code = subprocess.call(cmd, shell=True)
    if code > 1:
        raise Exception("'{}' exec failed，return code：{}".format(cmd, code))


if __name__ == '__main__':
    dt = datetime.datetime.now()
    msg = dt.strftime("%Y%m%d%H%M")

    run_cmd("git add *")
    run_cmd("git commit -a -m {}".format(msg))
    run_cmd("git push origin main")
