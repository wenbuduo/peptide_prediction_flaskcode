import re
import os

from flask import Blueprint, request, jsonify


# 设置上传目录
UPLOAD_FOLDER = 'uploads'

# 创建文件相关的蓝图
input_bp = Blueprint('input', __name__)



@input_bp.route("/detail", methods=["GET"])
def get_detail_of_PSMID():
    """
    模型输入详细信息查看
    """
    # 获取查询参数
    filename = request.args.get('filename')  # 获取 filename 参数
    PSM_ID = request.args.get('PSM_ID')  # 获取 PSM_ID 参数

    # 确保 PSM_ID 是整数
    try:
        PSM_ID = int(PSM_ID)
    except ValueError:
        return jsonify({"error": "Invalid PSM_ID, it must be an integer."}), 400

    # 检查 filename 是否存在
    if not filename:
        return jsonify({"error": "Filename is required."}), 400

    # 解析文件
    try:
        psm_data = parse_mgf(filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # 检查 PSM_ID 是否在有效的范围内
    if PSM_ID < 1 or PSM_ID > len(psm_data):
        return jsonify({"error": f"PSM_ID {PSM_ID} is out of range. Valid range: 1-{len(psm_data)}."}), 400

    # 获取对应 PSM_ID 的数据，索引为 PSM_ID - 1
    res_data = psm_data[PSM_ID - 1]

    # 返回转换后的字典
    return jsonify(res_data)


def parse_mgf(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    spectra = []
    current_spectrum = []
    spectrum_info = {}

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith('BEGIN IONS'):
            # 开始新的谱图
            current_spectrum = []
            spectrum_info = {}  # 每个谱图的信息字典清空
        elif line.startswith('END IONS'):
            # 完成当前谱图的读取，将其加入结果
            if current_spectrum:
                spectrum_info['spectrum'] = current_spectrum
                spectra.append(spectrum_info)
            current_spectrum = []
        elif '=' in line:
            # 提取谱图头部信息（如 TITLE, PEPMASS, CHARGE 等）
            key, value = line.split('=', 1)
            spectrum_info[key.strip()] = value.strip()
        else:
            # 读取 m/z 和 intensity 的值
            match = re.match(r"(\d+\.\d+)\s+(\d+\.\d+)", line)
            if match:
                mz = float(match.group(1))
                intensity = float(match.group(2))
                current_spectrum.append({'mz': mz, 'intensity': intensity})
    return spectra
