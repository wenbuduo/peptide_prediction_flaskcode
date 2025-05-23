import asyncio
from flask_socketio import SocketIO, emit
from flask import Flask, jsonify, request
from flask_cors import CORS
from blueprints import register_blueprints  # 导入蓝图注册函数
from socket_set.socket_listeners import setup_socketio_listeners


async_mode = None

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 注册蓝图
register_blueprints(app)

# 初始化 SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# 注册所有的SocketIO事件监听器
setup_socketio_listeners(socketio)



# 首页测试接口
@app.route('/')
def home():
    return jsonify({"message": "Casanovo prediction API is running!"})


# 启动服务器
if __name__ == '__main__':
    # 允许使用不安全的Werkzeug（仅限开发环境）
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
