#!/usr/bin/env python3
# coding: utf-8

# maintainer: tangmingming@hellobike.com

# 替换项目名
# 重新生成SECRET_KEY
# 删除git远程仓库

import subprocess

from django.core.management.utils import get_random_secret_key


OLD_PROJECT_NAME = "AppSpexBackend"


def replace_secret_key():
    NEW_SECRET_KEY = get_random_secret_key()
    content = ""
    print("开始替换secret key...")
    with open(f"{OLD_PROJECT_NAME}/settings.py", "r") as f:
        for line in f.readlines():
            if line.startswith("SECRET_KEY"):
                line = f"SECRET_KEY = '{NEW_SECRET_KEY}'"
            content += line
    with open(f"{OLD_PROJECT_NAME}/settings.py", "w") as f:
        f.writelines(content)
    print(f"new secret key: {NEW_SECRET_KEY}")
            

def run_cmd(cmd):
    code = subprocess.call(cmd, shell=True)
    if code != 0:
        raise Exception("'{}' 执行失败，返回code：{}".format(cmd, code))


if __name__ == '__main__':
    new_project_name = input("新项目名:")
    replace_secret_key()
    run_cmd(f"mv ../{OLD_PROJECT_NAME} ../{new_project_name}")
    print(f"已将根目录重命名为: {new_project_name}")
    run_cmd(f"mv {OLD_PROJECT_NAME} {new_project_name}")
    print(f"已将子目录{OLD_PROJECT_NAME} 重命名为 {new_project_name}")
    run_cmd(f"grep '{OLD_PROJECT_NAME}' -rl ./* --exclude-dir='__pycache__' | xargs sed -i '' 's/{OLD_PROJECT_NAME}/{new_project_name}/'")
    print(f"项目中所有文件中的{OLD_PROJECT_NAME} 替换为 {new_project_name}")
    run_cmd("git remote remove origin")
    print("初始化成功")

