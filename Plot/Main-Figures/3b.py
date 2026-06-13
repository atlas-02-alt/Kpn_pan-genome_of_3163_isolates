import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# 全局字体设置
mpl.rcParams.update({
    'font.family': 'Arial',            # 强制使用 Arial
    'axes.unicode_minus': False,       # 解决负号乱码
    'pdf.fonttype': 42, 'ps.fonttype': 42
})

# 读取数据
path = "C:/Users/yxLig/Nutstore/1/我的坚果云 (2)/Klebsiella_pneumoniae/Figures-re/fig4部分相关数据/a-candidates_distribution.xlsx"
df = pd.read_excel(path, sheet_name='med', index_col=0)

# 选择两列（这里假设选择前两列，你可以根据需要修改）
selected_columns = df.columns[0:2]  # 修改这里选择你需要的列
df_selected = df[selected_columns]

# 手动指定每行的颜色列表（根据你的需求指定颜色）
row_colors = ['#377EB8', '#377EB8', '#377EB8', '#377EB8', '#B23648', '#B23648', '#B23648', '#DC7369', '#DC7369',
              '#D8EBCD', '#D8EBCD', '#D8EBCD', '#F8EFB5', '#DAD4B9', '#DAD4B9', '#C8CDCF', '#E1F3FA']
#row_colors = ['#377EB8', '#B23648', '#DC7369', '#D8EBCD', '#F8EFB5', '#DAD4B9', '#C8CDCF', '#E1F3FA']

# 设置花纹样式
hatch_styles = ['', '/']  # 一些常见的花纹

# 单独生成两个图例句柄
legend_elements = [
    plt.Rectangle((0,0),1,1, facecolor='white', edgecolor='black', hatch='/', label='unknown'),
    plt.Rectangle((0,0),1,1, facecolor='white', edgecolor='black', hatch='', label='known')
]

# 画图
fig, ax = plt.subplots(figsize=(4, 6.3))
bottom = [0] * len(df_selected)
y_pos = range(len(df_selected))  # y轴位置

# 堆叠绘图
for idx, drug_class in enumerate(df_selected.columns):
    ax.barh(
        y=y_pos,
        width=df_selected[drug_class],
        left=bottom,
        height=0.8,
        color=row_colors,  # 每行使用指定颜色
        hatch=hatch_styles[idx % len(hatch_styles)],  # 根据列索引循环设置花纹
        edgecolor='black'  # 添加边框颜色
    )
    bottom = [i + j for i, j in zip(bottom, df_selected[drug_class])]

# 设置y轴标签
ax.set_yticks(y_pos)
ax.set_yticklabels(df_selected.index)

# 关键调整：设置上下边距为半个柱子高度
ax.set_ylim(-0.65, len(df_selected) - 0.35)

# 创建自定义图例，仅显示花纹样式
# 单独生成两个图例句柄
legend_elements = [
    plt.Rectangle((0,0),1,1, facecolor='white', edgecolor='black', hatch='', label='known'),
    plt.Rectangle((0,0),1,1, facecolor='white', edgecolor='black', hatch='/', label='unknown')
]

#ax.legend(handles=legend_elements, loc='upper right')

# 标签与图例
ax.set_xlabel("selected candidates")
ax.set_title("v-features distribution")

ax.invert_yaxis()
plt.tight_layout()
plt.show()