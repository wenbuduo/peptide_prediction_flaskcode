import os


from flask import Blueprint, request, jsonify, send_file
from datetime import datetime

# 创建文件相关的蓝图
file_bp = Blueprint('file', __name__)

# 设置上传目录和结果目录
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'



@file_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    文件上传接口
    """
    if 'file' not in request.files:
        return jsonify({"error": "没有文件上传！"}), 400

    file = request.files['file']
    if file:
        # 获取文件扩展名（如果有的话）
        file_extension = os.path.splitext(file.filename)[1]

        # 获取当前时间并格式化为 yyyymmdd_hhmmss 格式
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 使用当前时间作为文件名，并保留文件扩展名
        unique_filename = f"{current_time}{file_extension}"

        if file.filename.__contains__("user_input"):
            unique_filename = "user_input_" + unique_filename

        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)  # 保存文件到指定目录

        # 返回上传成功的响应
        return jsonify({
            "message": "文件上传成功！",
            "uploaded_file": unique_filename
        })

    return jsonify({"error": "文件格式不正确，仅支持 .mgf 文件！"}), 400


@file_bp.route('/download', methods=['GET'])
def download_file():
    # 获取查询参数
    filename = request.args.get('filename')  # 获取 filename 参数
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    # 检查文件是否存在
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404
