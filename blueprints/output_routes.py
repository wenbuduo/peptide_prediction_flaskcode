import json
import os
from flask import Blueprint, request, jsonify

# 设置上传目录
RESULT_FOLDER = 'results'

# 创建预测相关的蓝图
output_bp = Blueprint('output', __name__)

@output_bp.route('/detail', methods=['GET'])
def get_detail():
    filename = request.args.get('filename')  # 获取 filename 参数

    try:
        psm_data = parse_mztab_file(filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return json.dumps(psm_data, indent=4)


@output_bp.route('/sequence', methods=['GET'])
def parse_sequence(filename):
    # 获取 psm_data
    psm_data = parse_mztab_file(filename)
    # 提取所有的 sequence 字段
    sequences = [psm['sequence'] for psm in psm_data if 'sequence' in psm]

    # 将所有的 sequence 用回车符拼接起来
    result = '\n'.join(sequences)
    # print(sequences)
    return result


# 读取mztab文件
def parse_mztab_file(filename):
    #
    file_path = os.path.join(RESULT_FOLDER, filename)
    # 打开文件并读取所有内容
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 去除文件中的空行和多余的换行符
    lines = [line.strip() for line in lines if line.strip()]

    # 查找 PSM 部分的开始位置，确保文件中有 'PSH' 行
    try:
        psh_line_index = next(i for i, line in enumerate(lines) if line.startswith('PSH'))
    except StopIteration:
        raise ValueError("文件中未找到以 'PSH' 开头的行，无法解析 PSM 部分。")

    psm_lines = lines[psh_line_index:]  # 获取 PSM 行数据

    # 提取表头（第一行）作为字段名
    fields = psm_lines[0].split('\t')

    # 处理 PSM 行数据
    psm_data = []
    for line in psm_lines[1:]:
        values = line.split('\t')
        psm_dict = dict(zip(fields, values))  # 使用第一行的字段名作为key，后续每行的值作为value
        psm_data.append(psm_dict)

    # 遍历每个字典并修改键名
    for item in psm_data:
        if "search_engine_score[1]" in item:
            item["score"] = item["search_engine_score[1]"]

    return psm_data


