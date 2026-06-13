import pandas as pd
from scipy import stats

# 读取文件
file_path="C:/Users/yxLig/Nutstore/1/我的坚果云 (2)/Klebsiella_pneumoniae/Figures-re/fig4部分相关数据/cd-ablation_cmp - 副本.xlsx"
df = pd.read_excel(file_path,sheet_name='Sheet1')
df = df.iloc[:, 2:]
df.set_index(df.columns[0], inplace=True)

# 检验known的时候要放掉NIT
df = df[df.index != 'NIT']

# 示例：假设数据列的名称是 'Column_A' 和 'Column_B'
Column_A='test-auc'
Column_B='dis-test-auc'
column_a = df[Column_A]
column_b = df[Column_B]

# **Mann-Whitney U检验**：检验两组数据的分布是否有显著差异
# 这里的零假设是两组数据来自相同的分布
u_stat, p_value_u = stats.mannwhitneyu(column_a, column_b, alternative='greater')

# 计算方差
var_a = column_a.var(ddof=1)  # 样本方差
var_b = column_b.var(ddof=1)

# 打印结果
print(f"Mann-Whitney U检验的统计量：{u_stat}")
print(f"Mann-Whitney U检验的p值：{p_value_u}")
if p_value_u < 0.05:
    print("两组数据的分布存在显著差异")
else:
    print("两组数据的分布不存在显著差异")