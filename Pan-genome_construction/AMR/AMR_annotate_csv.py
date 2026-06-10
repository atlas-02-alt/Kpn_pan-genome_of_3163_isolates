import pandas as pd

# 输入文件
panaroo_csv = "/data/home/sfwang/kpn/Panaroo/both-align-results-strict-adv/gene_presence_absence.csv"
abricate_files = {
    "CARD": "./AMR_annotation/both_card_results_longCentroidID.tab",
    "NCBI": "./AMR_annotation/both_ncbi_results_longCentroidID.tab",
    "ResFinder": "./AMR_annotation/both_resfinder_results_longCentroidID.tab"
}
#output_all = "./both-align-results-strict/panaroo_with_resistance_all.csv"
output_filtered = "./both-align-results-strict-adv/amr_gene_presence_absence_longCentroidID.csv"

# 读取 panaroo 输出，加上 low_memory=False 避免 dtype 警告
df = pd.read_csv(panaroo_csv, low_memory=False)

# 依次处理每个 abricate 文件
for db_name, ab_file in abricate_files.items():
    print(f"正在处理 {db_name} 数据库: {ab_file}")
    
    # 读 abricate 文件
    ab_df = pd.read_csv(ab_file, sep="\t", header=None)
    
    # 取第2列(基因名)和第6列(耐药基因名)
    ab_map = dict(zip(ab_df.iloc[:, 1], ab_df.iloc[:, 5]))
    print(ab_map)
    
    # 在 panaroo 表里新增一列
    df[db_name] = df["Gene"].map(ab_map)

# -------- 调整列顺序：把 AMR 三列放最前面 --------
amr_cols = list(abricate_files.keys())  # ["CARD", "NCBI", "ResFinder"]
other_cols = [c for c in df.columns if c not in amr_cols]
df = df[amr_cols + other_cols]

# 保存完整表格（含耐药注释）
#df.to_csv(output_all, index=False)

# 保留至少一个数据库有命中
filtered_df = df[df[list(abricate_files.keys())].notna().any(axis=1)]

# 保存过滤后的表格
filtered_df.to_csv(output_filtered, index=False)

print(f"处理完成 ✅\n筛选表格: {output_filtered}")
