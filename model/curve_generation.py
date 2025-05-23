# 设置上传目录和结果目录
import os

import pandas as pd

from blueprints.input_routes import parse_mgf
from blueprints.output_routes import parse_mztab_file

import depthcharge
import matplotlib
matplotlib.use('Agg')  # 强制使用 Agg 后端

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import auc


from casanovo.denovo import evaluate


# 修改工作目录到项目根目录
new_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(new_directory)

AUC_FOLDER = 'AUCs'
# 确保auc目录存在
os.makedirs(AUC_FOLDER, exist_ok=True)

# `psm_sequences` is assumed to be a DataFrame with at least the following
# three columns:
#   - "sequence": The ground-truth peptide labels.
#   - "sequence_pred": The predicted peptide labels.
#   - "search_engine_score[1]": The prediction scores.
def get_psm_sequences(upload_filename, result_filename):

    mgf_data = parse_mgf(upload_filename)
    mztab_data = parse_mztab_file(result_filename)
    sequence_true = []
    sequence_pred = []
    score = []

    # 提取每个谱图的 SEQ 信息作为 "sequence" 列
    for spectrum in mgf_data:
        sequence_true.append(spectrum["SEQ"])
    for spectrum in mztab_data:
        sequence_pred.append(spectrum["sequence"])
        score.append(spectrum["search_engine_score[1]"])
    # 创建 DataFrame
    psm_sequences = pd.DataFrame({
        "sequence": sequence_true,
        "sequence_pred": sequence_pred,  # 预测的序列列
        "search_engine_score[1]": score  # 预测得分列
    })

    psm_sequences["search_engine_score[1]"] = psm_sequences["search_engine_score[1]"].astype(float)
    return psm_sequences

def print_auc(filename):
    filename = filename.split(".")[0]
    print(filename)
    upload_filename = f"{filename}.mgf"
    result_filename = f"results_{filename}.mztab"
    psm_sequences = get_psm_sequences(upload_filename, result_filename)
    # 排序，按得分降序
    psm_sequences = psm_sequences.sort_values("search_engine_score[1]", ascending=False)
    # 获取匹配结果
    aa_matches_batch = evaluate.aa_match_batch(
        psm_sequences["sequence"],
        psm_sequences["sequence_pred"],
        depthcharge.masses.PeptideMass("massivekb").masses,
    )
    # 计算精度和覆盖率
    peptide_matches = np.asarray([aa_match[1] for aa_match in aa_matches_batch[0]])
    precision = np.cumsum(peptide_matches) / np.arange(1, len(peptide_matches) + 1)
    coverage = np.arange(1, len(peptide_matches) + 1) / len(peptide_matches)
    # 计算匹配阈值
    threshold = np.argmax(psm_sequences["search_engine_score[1]"] < 0.1)  # 修改阈值为 0.1 或其他合理的值
    # 打印精度和覆盖率
    print(f"Peptide precision = {precision[threshold]:.3f}")
    print(f"Coverage = {coverage[threshold]:.3f}")
    print(f"Peptide precision @ coverage=1 = {precision[-1]:.3f}")

    # 绘制精度-覆盖率曲线
    width = 4
    height = width / 1.618
    fig, ax = plt.subplots(figsize=(width, width))

    ax.plot(
        coverage, precision, label=f"Casanovo AUC = {auc(coverage, precision):.3f}"
    )
    ax.scatter(
        coverage[threshold],
        precision[threshold],
        s=50,
        marker="D",
        edgecolors="black",
        zorder=10,
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax.set_xlabel("Coverage")
    ax.set_ylabel("Peptide precision")
    ax.legend(loc="lower left")

    # 保存图像
    png_filename = f"{filename}.png"
    file_path = os.path.join(AUC_FOLDER, png_filename)
    plt.savefig(file_path, dpi=300, bbox_inches="tight")
    plt.close()

    return png_filename


