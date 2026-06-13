import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from statannotations.Annotator import Annotator

# 读取文件
file_path = "C:/Users/yxLig/Nutstore/1/我的坚果云 (2)/Klebsiella_pneumoniae/Figures-re/fig4部分相关数据/cd-ablation_cmp.xlsx"
df = pd.read_excel(file_path,sheet_name='Sheet1')
columns_to_plot = ['test-auc', 'known-test-auc', 'validation-auc', 'known-vali-auc']
df = df.iloc[:, 2:]
df.set_index(df.columns[0], inplace=True)
df = df[columns_to_plot]
df = df.rename(columns={'test-auc': "test-Total", 
                        'known-test-auc': "test-Known",
                        'validation-auc': "validate-Total",
                        'known-vali-auc': "validate-Known"})
print(df.shape)

# 自定义每个箱线图的颜色
box_colors = ['#7db3c6', '#ddc4e2', '#7db3c6', '#ddc4e2']

# 绘制箱线图
plt.figure(figsize=(8.3, 6))
sns.boxplot(data=df, palette=box_colors, showfliers=False, width=0.45)

# 显示每个数据点，使用黑色实心点
sns.stripplot(data=df, color='black', jitter=False, size=4, alpha=0.6)

# 连接两个test列和两个vali列
for i in range(len(df)):
    # 连接 test-Total 和 test-Known
    plt.plot([0, 1], [df.iloc[i, 0], df.iloc[i, 1]], color='gray', linewidth=0.5, alpha=0.3, zorder=0)
    # 连接 validate-Total 和 validate-Known
    plt.plot([2, 3], [df.iloc[i, 2], df.iloc[i, 3]], color='gray', linewidth=0.5, alpha=0.3, zorder=0)

# 显示图形
plt.ylim(0.3, 1.1)
plt.show()
