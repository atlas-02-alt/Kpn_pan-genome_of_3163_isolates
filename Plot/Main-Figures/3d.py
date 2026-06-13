import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# 读取文件
file_path="C:/Users/yxLig/Nutstore/1/我的坚果云 (2)/Klebsiella_pneumoniae/Figures-re/fig4部分相关数据/cd-ablation_cmp.xlsx"
df = pd.read_excel(file_path,sheet_name='Sheet1')
df = df.iloc[:, 2:]
df.set_index(df.columns[0], inplace=True)
columns_to_plot = ['test-auc', 'core-test-auc', 'dis-test-auc', 'validation-auc', 'core-vali-auc', 'dis-vali-auc']
df = df[columns_to_plot]
df = df.rename(columns={'test-auc': 'test-Total', 
                        'core-test-auc': 'test-Core', 
                        'dis-test-auc': 'test-Dispensable',
                        'validation-auc': 'validate-Total',
                        'core-vali-auc': 'validate-Core',
                        'dis-vali-auc': 'validate-Dispensable'})
print(df.shape)

# 自定义每个箱线图的颜色
box_colors = ['#7db3c6', '#a58faa', '#334a52', '#7db3c6', '#a58faa', '#334a52']

# 绘制箱线图
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, palette=box_colors, showfliers=False, width=0.45)

# 显示每个数据点，使用黑色实心点
sns.stripplot(data=df, color='black', jitter=False, size=4, alpha=0.6)

# 显示图形
plt.ylim(0.3, 1.1) 
plt.show()