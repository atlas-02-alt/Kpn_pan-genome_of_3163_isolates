import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

# 数据
data = np.array([
    [1768, 7],
    [119, 7]
])

# 创建图（宽 > 高，做成扁一点的长方形）
fig, ax = plt.subplots(figsize=(8, 3))   # <<< 扁长比例在这里调

ax.axis('off')

# 创建表格
table = ax.table(
    cellText=data,
    cellLoc='center',
    loc='center'
)

# 调整单元格大小
table.scale(2.1, 2.5)   # <<< 第一个是宽度缩放，第二个是高度缩放

# 美化样式
for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor('black')
    cell.set_linewidth(2)
    cell.set_fontsize(20)

plt.tight_layout()

# 如果要保存 PDF：
save_path = "C:\\Users\\yxLig\\Nutstore\\1\\我的坚果云 (2)\\Klebsiella_pneumoniae\\Figures-re\\fig5"
plt.savefig(save_path + "\\5d-ompA-NIT-LorData.pdf", format="pdf", bbox_inches="tight")

plt.show()
