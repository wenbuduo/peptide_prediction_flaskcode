import json
import re
import subprocess
import sys
import time
from flask_socketio import SocketIO

# 每隔多少秒发送一次进度
TIME_TO_PRINT = 1

def send_progress(socketio, progress, speed, sid):
    """通过 socketio 向客户端发送进度和速度信息 (JSON格式)"""
    # 创建一个字典，包含进度和速度信息
    progress_data = {
        'progress': progress,
        'speed': speed  # 包含速度信息 (it/s)
    }

    # 将字典发送到客户端，使用 JSON 格式
    socketio.emit('prediction', json.dumps(progress_data), room=sid)


def run_with_progress(command, socketio, sid=None):
    """运行命令并通过 socketio 向客户端发送进度和速度"""

    # 启动子进程并捕获输出，指定编码为 UTF-8
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,  # 启用文本模式
        bufsize=1,
        encoding='utf-8'  # 显式指定编码为 UTF-8
    )

    # 正则表达式，匹配进度条信息和速度
    progress_pattern = re.compile(r"Predicting DataLoader \d+:.*\s(\d+)%.*?(\d+\.\d+)it/s")

    last_output_time = time.time()

    try:
        # 持续读取进度条输出
        while True:
            # 读取每一行输出
            output = process.stdout.readline()

            if output == '' and process.poll() is not None:
                break

            if output:
                # 查找进度信息和速度
                progress_match = progress_pattern.search(output)
                if progress_match:
                    progress = int(progress_match.group(1))  # 进度百分比
                    speed = float(progress_match.group(2))  # 速度 (it/s)

                    # 每隔5秒输出一次进度和速度
                    current_time = time.time()
                    if current_time - last_output_time >= TIME_TO_PRINT:
                        last_output_time = current_time
                        sys.stdout.write(f"\rProgress: {progress}% Speed: {speed} it/s")
                        sys.stdout.flush()

                        # 如果 socketio 连接存在，发送进度和速度
                        if socketio:
                            send_progress(socketio, progress, speed, sid)
                            print(f"send {progress}% at {speed} it/s to {sid}")
                        else:
                            print("no socket_set")

        # 等待命令执行完毕并获取输出
        stdout, stderr = process.communicate()

        # 输出结果
        if stdout:
            print(stdout)
        if stderr:
            print(stderr)

    except Exception as e:
        print(f"Error: {e}")

