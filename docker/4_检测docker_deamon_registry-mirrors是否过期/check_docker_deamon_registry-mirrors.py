#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
作者: sinvon
创建时间: 2024年12月18日21:36:56

脚本名称: check_docker_deamon_registry-mirrors.py

脚本作用:
    本脚本用于检测 Docker 配置文件 (/etc/docker/daemon.json) 中的 `registry-mirrors` 配置项。
    它将检查 `registry-mirrors` 列表中的每个 URL 地址是否可访问，并根据访问结果输出绿色（成功）或红色（失败）的消息。
    可以帮助运维人员和开发者快速验证 Docker 镜像源的可用性，确保 Docker 配置正确且能够顺利拉取镜像。

使用方式:
    1. 确保脚本有权限访问 `/etc/docker/daemon.json` 文件。
    2. 运行脚本时，脚本会自动读取 Docker 配置文件中的 `registry-mirrors` 字段。
    3. 脚本会尝试访问每个 URL，并输出每个镜像源的访问状态。
    4. 如果没有配置 `registry-mirrors`，脚本会输出相应的提示信息。

    执行命令：
    python3 check_docker_deamon_registry-mirrors.py

注意:
    - 如果脚本没有权限读取 `/etc/docker/daemon.json`，请使用 `sudo` 运行。
    - 如果出现网络问题，无法访问某些镜像源，脚本会显示失败状态。

"""

import json
import requests
import os

# ANSI颜色码
RED = '\033[31m'  # 红色
GREEN = '\033[32m'  # 绿色
RESET = '\033[0m'  # 重置颜色

# 读取 /etc/docker/daemon.json 文件，获取 registry-mirrors 列表
def read_daemon_json():
    """
    读取 Docker 配置文件 (/etc/docker/daemon.json) 并解析出 `registry-mirrors` 字段的值。
    返回值是一个包含镜像源 URL 字符串的列表。
    """
    daemon_json_path = '/etc/docker/daemon.json'
    
    if not os.path.exists(daemon_json_path):
        print(f"{RED}Error: {daemon_json_path} does not exist.{RESET}")
        return []

    with open(daemon_json_path, 'r') as file:
        try:
            data = json.load(file)
            # 获取 registry-mirrors 字段中的 URL 列表
            registry_mirrors = data.get('registry-mirrors', [])
            print(f"Found registry-mirrors: {registry_mirrors}")  # 调试输出
            return registry_mirrors
        except json.JSONDecodeError:
            print(f"{RED}Error: Failed to parse {daemon_json_path}.{RESET}")
            return []

# 检查 URL 是否可以访问
def check_url(url):
    """
    检查给定的 URL 是否可访问。
    使用 HTTP GET 请求访问 URL，成功返回 True，失败返回 False。
    """
    try:
        response = requests.get(url, timeout=5)  # 设置超时时间为 5 秒
        if response.status_code == 200:
            return True
    except requests.RequestException:
        pass
    return False

# 打印带有颜色的结果
def print_result(url, success):
    """
    根据 URL 的访问结果输出带有颜色的消息。
    如果成功，显示绿色；如果失败，显示红色。
    """
    if success:
        print(f"{GREEN}[SUCCESS] {url}{RESET}")
    else:
        print(f"{RED}[FAILURE] {url}{RESET}")

def main():
    """
    主函数，读取配置文件中的 `registry-mirrors` URL 列表并逐一检查它们的可访问性。
    根据每个 URL 的检查结果，输出对应的成功或失败消息。
    """
    # 读取 Docker 配置文件并获取 registry-mirrors 列表
    urls = read_daemon_json()

    if not urls:
        print(f"{RED}No registry-mirrors to check. Exiting...{RESET}")
        return

    # 遍历所有的 registry-mirrors URL，逐一检查访问状态
    for url in urls:
        print('----------------------------------')
        print(f"Checking: {url}")
        success = check_url(url)
        print_result(url, success)

if __name__ == "__main__":
    main()

