import os
import threading
import time
from datetime import datetime
from flask import Blueprint, request, jsonify

from model.casanovo_model import CasanovoModel

text_bp = Blueprint('text', __name__)

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

MODELS = {
    "casanovo": CasanovoModel()
}

@text_bp.route('/clear-on-refresh', methods=['POST'])
def clear_on_refresh():
    """
    页面刷新时调用，清理 uploads、results、AUCs 文件夹中的所有文件。
    """
    folders = ['uploads', 'results', 'AUCs']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        folder_path = os.path.abspath(folder)
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"Deleted on refresh: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")
    return jsonify({"message": "刷新清理成功"}), 200

@text_bp.route('/predict', methods=['POST'])
def predict_text():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "未提供输入文本！"}), 400

    input_text = data['text']
    model_name = data['model']
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    mgf_filename = f"text_{current_time}.mgf"
    mgf_filepath = os.path.join(UPLOAD_FOLDER, mgf_filename)

    try:
        with open(mgf_filepath, 'w') as mgf_file:
            mgf_file.write(input_text)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    try:
        model = MODELS[model_name]
        if not model.is_loaded():
            return jsonify({"error": f"模型 '{model_name}' 未正确加载，请检查模型初始化！"}), 500
        prediction_result = model.predict_from_file(mgf_filename)
        return jsonify({
            "message": "预测完成！",
            "model": model_name,
            "uploaded_file": mgf_filename,
            "result_file": f"result_{mgf_filename}.mztab",
            "prediction": prediction_result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
