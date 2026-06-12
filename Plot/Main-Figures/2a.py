import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import matplotlib as mpl

mpl.rcParams['font.family'] = 'Arial'

def read_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    data = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 2:
            strain, n50 = parts[0], float(parts[1])
            data.append((strain, n50))
    return data
# 读取数据
data1 = read_data("C:/Users/yxLig/Nutstore/1/我的坚果云 (2)/Klebsiella_pneumoniae/figures-trial/fig2-中间文件/Contig_n50_1174.txt")
data2 = read_data("C:/Users/yxLig/Nutstore/1/我的坚果云 (2)/Klebsiella_pneumoniae/figures-trial/fig2-中间文件/Contig_n50_491.txt")

# 合并数据，附加来源标签
all_data = [(x[0], x[1], 'Pure short-read assembly') for x in data1] + \
           [(x[0], x[1], 'Hybrid long+short-read assembly') for x in data2]

# 按contig N50从大到小排序
all_data_sorted = sorted(all_data, key=lambda x: x[1], reverse=True)

# 提取排序后数据
n50_values = [x[1] for x in all_data_sorted]
sources = [x[2] for x in all_data_sorted]
x = np.arange(len(all_data_sorted))

# 根据来源给颜色
color_map = {'Pure short-read assembly': '#91CAE8', 'Hybrid long+short-read assembly': '#F48892'}
colors = [color_map[src] for src in sources]

fig, ax = plt.subplots(figsize=(12,6), dpi=100)

# 这里设置柱宽，默认是0.8，改成0.9或1更宽，柱子之间间隙小
bar_width = 1
bars = ax.bar(x, n50_values, color=colors, width=bar_width)
#bars = ax.bar(x, n50_values, color=colors)

ax.set_xticks([])
ax.set_ylabel('Contig N50')

# 调整x轴范围，让柱子更靠边，x轴范围左右扩展0.5个单位
ax.set_xlim(-0.5, len(all_data_sorted) - 0.5)

legend_elements = [Patch(facecolor='#91CAE8', label='pure short-read assembly'),
                   Patch(facecolor='#F48892', label='hybrid long+short-read assembly')]
ax.legend(handles=legend_elements, loc='upper right')

plt.tight_layout()
plt.show()
