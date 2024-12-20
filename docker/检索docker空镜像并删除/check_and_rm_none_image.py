#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
作者: sinvon
创建时间: 2024年12月18日21:35:48

脚本名称: check_and_rm_none_image.py

功能描述:
    1. 检测用户的终端类型（Shell 类型），适配不同终端（支持 bash 和 fish）。
    2. 删除已停止的 Docker 容器，释放系统资源。
    3. 清理无用的 Docker 镜像，减少磁盘空间占用。
    4. 清理悬空（孤立）镜像，保持 Docker 环境整洁。
    5. 显示当前 Docker 容器和镜像的状态，便于用户查看清理结果。
    6. 该脚本设计为通用型工具，可用于自动化清理脚本，适合日常维护 Docker 环境。
"""

import os
import subprocess


def cut_line():
    print("===========================================")


def detect_shell():
    """检测用户当前的 Shell 类型"""
    shell_path = os.environ.get("SHELL", "/bin/bash")
    if "fish" in shell_path:
        return "fish"
    elif "bash" in shell_path:
        return "bash"
    else:
        print(f"未知的 Shell 类型，默认使用 bash: {shell_path}")
        return "bash"


def run_command(command, shell_type):
    """运行适配指定 Shell 的命令"""
    try:
        # 如果是 fish，需要通过 fish 执行
        if shell_type == "fish":
            command = f"fish -c '{command}'"
        result = subprocess.run(command, shell=True,
                                text=True, capture_output=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e.stderr.strip()}")
        return None


def remove_exited_containers(shell_type):
    """删除所有已停止的容器"""
    print("正在删除已停止的容器...")
    exited_containers = run_command(
        "docker ps -a -f 'status=exited' -q", shell_type)
    if exited_containers:
        run_command(f"docker rm {exited_containers}", shell_type)
        print("已停止的容器删除完成")
    else:
        print("没有已停止的容器需要删除")


def prune_images(shell_type):
    """清理所有无用的镜像"""
    print("正在清理无用镜像...")
    run_command("docker image prune -a -f", shell_type)
    print("无用镜像清理完成")


def remove_dangling_images(shell_type):
    """清理悬空镜像"""
    print("正在清理悬空镜像...")
    dangling_images = run_command(
        "docker images -f 'dangling=true' -q", shell_type)
    if dangling_images:
        run_command(f"docker rmi {dangling_images}", shell_type)
        print("悬空镜像清理完成")
    else:
        print("没有悬空镜像需要清理")


def show_docker_status(shell_type):
    """显示 Docker 镜像和容器状态"""
    print("\n当前 Docker 容器状态:")
    print(run_command("docker ps -a", shell_type))
    print("\n当前 Docker 镜像状态:")
    print(run_command("docker images", shell_type))


if __name__ == "__main__":
    print("Docker 清理脚本启动...")
    shell_type = detect_shell()
    print(f"检测到的 Shell 类型: {shell_type}")
    remove_exited_containers(shell_type)
    prune_images(shell_type)
    remove_dangling_images(shell_type)
    show_docker_status(shell_type)
    print("清理完成！")
