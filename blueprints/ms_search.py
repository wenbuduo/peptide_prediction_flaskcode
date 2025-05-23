from flask import jsonify, request, Blueprint
import pandas as pd

# 创建蓝图
ms_search = Blueprint('ms_search', __name__)

# 读取 CSV 数据
df = pd.read_csv('./static/ms_search.csv')

# 每页显示的数据条数
PAGE_SIZE = 10

# 定义 API 路由，获取符合搜索条件的化合物
@ms_search.route('/', methods=['GET'])
def get_compounds():
    search_query = request.args.get('search', '')  # 获取查询参数
    search_type = request.args.get('searchType', 'Name')  # 默认按名称搜索
    page = int(request.args.get('page', 1))  # 当前页，默认是第一页
    offset = (page - 1) * PAGE_SIZE  # 计算偏移量

    # 根据查询条件过滤数据
    if search_query:
        if search_type == 'Name':
            filtered_df = df[df['Name'].str.contains(search_query, case=False, na=False)]
        elif search_type == 'SMILES':
            filtered_df = df[df['SMILES'].str.contains(search_query, case=False, na=False)]
        else:
            filtered_df = df
    else:
        filtered_df = df  # 如果没有查询条件，返回所有数据

    # 分页：获取当前页的数据
    paginated_df = filtered_df.iloc[offset:offset + PAGE_SIZE]

    # 获取总数据条数，用于分页控件
    total = filtered_df.shape[0]

    # 将结果转换为字典格式并返回，包括总数据条数
    compounds = paginated_df[['id', 'SMILES', 'Name', 'MW']].to_dict(orient='records')
    return jsonify({
        'compounds': compounds,
        'total': total  # 返回总数据条数
    })
