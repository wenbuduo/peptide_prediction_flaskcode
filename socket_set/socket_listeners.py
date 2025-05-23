import os
import torch
from flask import request
from flask_socketio import SocketIO
from model.casanovo_model import CasanovoModel

# 设置上传目录
UPLOAD_FOLDER = 'uploads'

# 直接使用 CasanovoModel 进行预测
casanovo_model = CasanovoModel()


def setup_socketio_listeners(socketio: SocketIO):
    # 监听客户端连接事件
    @socketio.on('connect')
    def handle_connect():
        print("客户端已连接")
        sid = request.sid
        print(f"Client connected with sid: {sid}")
    def handle_predict_from_file(socketio, file_path, model, sid, device):
        try:
            # 调用模型进行预测，确保使用 GPU（如果可用）
            result = model.predict_from_file(file_path, socketio, sid, device)  # 预测完成后，将结果发送到客户端
            socketio.emit('result', result, room=sid)
        except Exception as e:
            # 错误处理
            socketio.emit('message', {'data': f"预测失败: {str(e)}"}, room=sid)
    # 监听客户端断开连接事件
    @socketio.on('disconnect')
    def handle_disconnect():
        print("客户端已断开连接")
    @socketio.on('prediction')
    def handle_prediction(data):
        # 获取文件名和设备参数
        filename = data.get('filename')
        device = data.get('device', '-1')  # 默认使用 CPU
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        # 获取当前 WebSocket 连接的 sid
        sid = request.sid
        # 向客户端发送一条消息，通知任务已开始
        socketio.emit('message', {'data': '预测任务已开始！'}, room=sid)
        # 使用 Casanovo 模型进行预测
        socketio.start_background_task(
            target=handle_predict_from_file,
            socketio=socketio,
            file_path=file_path,
            model=casanovo_model,  # 直接使用 casanovo_model
            sid=sid,
            device=device
        )
