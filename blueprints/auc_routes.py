# 创建auc相关的蓝图
from flask import Blueprint, send_from_directory, request

from model.curve_generation import print_auc

auc_bp = Blueprint('auc', __name__)
AUC_FOLDER = 'AUCs'


# 返回生成auc图的url
@auc_bp.route('/', methods=['GET'])
def upload_file():
    # 获取查询参数
    filename = request.args.get('filename')  # 获取 filename 参数

    png_filename = print_auc(filename)
    # 返回 aucs 目录中的指定文件
    return send_from_directory(AUC_FOLDER, png_filename)
