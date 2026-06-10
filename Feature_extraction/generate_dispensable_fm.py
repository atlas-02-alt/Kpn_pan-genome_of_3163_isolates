import os
import re
import json
import pandas as pd
from Bio import SeqIO

# 输入路径
input_dir = "/data/home/sfwang/kpn/Panaroo/both-align-results-strict-adv/dispensable_gene_sequences/"   # 修改为你的文件夹路径
mapping_json = "/data/home/sfwang/kpn/Panaroo/both-align-results-strict-adv/amr_panaroo_dict.json"  # 存放列名映射关系的 JSON 文件
output_csv = "/data/home/sfwang/kpn/Panaroo-DownStream-both/final_dispensable_fm.csv"

# 用正则提取组名：G 开头到第一个 ;
sample_pattern = re.compile(r"^(G[^;]+)")

gene_to_samples = {}

# 遍历所有 .aln.fas 文件
for filename in os.listdir(input_dir):
    if filename.endswith(".aln.fas"):
        gene_name = filename.replace(".aln.fas", "")
        file_path = os.path.join(input_dir, filename)
        
        samples = set()
        for record in SeqIO.parse(file_path, "fasta"):
            match = sample_pattern.search(record.id)
            if match:
                samples.add(match.group(1))
        
        gene_to_samples[gene_name] = samples

# 收集所有样本
all_samples = sorted({s for samples in gene_to_samples.values() for s in samples})

# 构建 0/1 矩阵
df = pd.DataFrame(0, index=all_samples, columns=gene_to_samples.keys())

for gene, samples in gene_to_samples.items():
    df.loc[list(samples), gene] = 1

# 读取映射关系并替换列名
if os.path.exists(mapping_json):
    with open(mapping_json, "r") as f:
        mapping = json.load(f)
    df.rename(columns=mapping, inplace=True)

# 检查每一列至少有 4 个 1 或者至少有 4 个 0， 过滤少数特征
rare_threshold = 3
bad_cols = [col for col in df.columns if df[col].sum() <= rare_threshold or df[col].sum() >= 3163-rare_threshold]
if bad_cols:
    print("以下列不足 4 个 1 或不足 4 个 0，请注意：")
    for col in bad_cols:
        print(f"{col}: {df[col].sum()} 个 1")

# 保存为 CSV
df.to_csv(output_csv)

print(f"结果已保存到 {output_csv}")
