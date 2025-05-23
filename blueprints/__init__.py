from flask import Blueprint

from .auc_routes import auc_bp
from .file_routes import file_bp
from .text_routes import text_bp
from .output_routes import output_bp
from .input_routes import input_bp
from .ms_search import ms_search


def register_blueprints(app):
    """注册所有的蓝图"""
    api_blueprint = Blueprint('api', __name__, url_prefix='/peptide-prediction')  # 应用级上下文
    # 注册蓝图
    api_blueprint.register_blueprint(file_bp, url_prefix='/file')  # 文件相关接口，带有 /file 前缀
    api_blueprint.register_blueprint(text_bp, url_prefix='/text')  # 文本预测相关接口，带有 /text 前缀
    api_blueprint.register_blueprint(output_bp, url_prefix='/output')  # 预测输出相关接口，带有 /output 前缀
    api_blueprint.register_blueprint(input_bp, url_prefix='/input')  # 模型输入相关接口，带有 /input 前缀
    api_blueprint.register_blueprint(auc_bp, url_prefix='/auc') # auc相关接口，带有/auc前缀
    api_blueprint.register_blueprint(ms_search, url_prefix='/ms_search')  # 质谱图信息检索相关接口，带有/ms_search前缀
    app.register_blueprint(api_blueprint)
