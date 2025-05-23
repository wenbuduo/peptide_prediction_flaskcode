import os
import subprocess
from blueprints.output_routes import parse_sequence
from utils.websocket import run_with_progress


class CasanovoModel:
    def __init__(self):
        """
        初始化 Casanovo 模型类
        """
        self.output_dir = "results"  # 定义输出目录
        os.makedirs(self.output_dir, exist_ok=True)  # 确保目录存在

    def predict_from_file(self, file_path, socketio=None, sid=None,device=None):
        """
        根据上传的 .mgf 文件进行预测
        :param file_path: 用户上传的 .mgf 文件的完整路径
        :param socketio: SocketIO 实例用于发送进度
        :param sid: WebSocket 连接的 sid
        :return: 预测结果（字符串）  结果文件名
        """
        print(f"模型预测的传入路径 {file_path}")
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件 {file_path} 不存在")
            filename = os.path.basename(file_path)
            filename = os.path.splitext(filename)[0]
            # 定义输出结果文件路径
            result_file_path = os.path.join(self.output_dir, f"results_{filename}.mztab")
            # 构建 Casanovo CLI 命令
            cmd = [
                "casanovo", "sequence",  # 调用 Casanovo 的预测功能
                "-o", result_file_path,  # 指定输出文件路径
                file_path  # 输入的 .mgf 文件

            ]
            # 运行命令并实时发送进度
            run_with_progress(cmd, socketio, sid)
            # 检查并读取输出结果文件内容
            if os.path.exists(result_file_path):
                result_file = os.path.basename(result_file_path)
                result_data = parse_sequence(result_file)
                return {"result_file": result_file, "result_data": result_data}
            else:
                return "预测失败: 无法找到结果文件"
        except subprocess.CalledProcessError as e:
            return f"预测失败: Casanovo 执行错误\n错误信息: {str(e)}"
        except FileNotFoundError as e:
            return f"预测失败: 文件不存在\n错误信息: {str(e)}"
        except Exception as e:
            return f"预测失败: 未知错误\n错误信息: {str(e)}"
