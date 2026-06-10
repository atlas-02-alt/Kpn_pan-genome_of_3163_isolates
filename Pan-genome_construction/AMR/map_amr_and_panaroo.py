import pandas as pd
import json

# 读取 CSV
df = pd.read_csv("/data/home/sfwang/kpn/Panaroo/both-align-results-strict-adv/amr_gene_presence_absence.csv")

# 在 AMR name 前加上前缀
df["AMR name"] = "amr_" + df["AMR name"].astype(str)

# 检查 AMR name 是否有重复
duplicates = df["AMR name"][df["AMR name"].duplicated()].unique()
if len(duplicates) > 0:
    print("⚠️ 发现重复的 AMR name：")
    for name in duplicates:
        print("  ", name)
else:
    print("✅ 没有发现重复的 AMR name")

# 构造字典
gene_dict = dict(zip(df["Gene"], df["AMR name"]))

# 保存为 JSON 文件
with open("./both-align-results-strict-adv/amr_panaroo_dict.json", "w") as f:
    json.dump(gene_dict, f, indent=4)

print("字典已保存到 ./both-align-results-strict-adv/amr_panaroo_dict.json")
