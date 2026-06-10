import os
import shutil

# 输入源文件夹和目标文件夹路径
src_dir = "/data/home/sfwang/kpn/Panaroo/both-align-results-strict-adv/core_gene_references/"           # 源文件夹
dst_dir = "/data/home/sfwang/kpn/Panaroo/both-align-results-strict-adv/alignment/"           # 目标文件夹

# 确保目标文件夹存在
os.makedirs(dst_dir, exist_ok=True)

for filename in os.listdir(src_dir):
    if filename.endswith(".fa"):
        # 去掉后缀
        name_without_suffix = filename[:-len(".fa")]

        # 创建对应的子文件夹
        subfolder = os.path.join(dst_dir, name_without_suffix)
        os.makedirs(subfolder, exist_ok=True)

        # 源文件路径
        src_path = os.path.join(src_dir, filename)

        # 目标文件路径（重命名为 ref.fa）
        dst_path = os.path.join(subfolder, "ref.fa")

        # 复制文件
        shutil.copy(src_path, dst_path)

print("比对用的参考序列分发完成！")
