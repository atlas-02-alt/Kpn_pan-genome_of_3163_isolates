import pandas as pd
import numpy as np

# === 读取数据 ===
fpath="C:\\Users\\yxLig\\Nutstore\\1\\我的坚果云 (2)\\Klebsiella_pneumoniae\\Figures-re\\fig5相关数据\\5a-group_258.csv"
features = pd.read_csv(fpath, index_col=0)
ppath="C:\\Users\\yxLig\\Nutstore\\1\\我的坚果云 (2)\\Klebsiella_pneumoniae\\Figures-re\\fig5相关数据\\supplement\\phenotypes_3163.csv"
phenotypes = pd.read_csv(ppath, index_col=0)

# === 设置目标基因（你要画哪一个）===
target_gene = '534_C->G'  # ← 改成你要分析的那个基因名
selected_antibiotics = ['SXT']  # ← 手动挑选

# === 计算每种抗生素的 log2 odds ratio ===
results = []
for i in range(0,1,1): #抗生素个数
    abx=selected_antibiotics[i]
    if abx not in phenotypes.columns:
        print(f"[警告] 抗生素 {abx} 不在 phenotypes.csv 中，跳过")
        continue

    df = features[[target_gene]].join(phenotypes[[abx]])
    df = df[df[abx].isin(['R', 'S'])].dropna()
    df = df.rename(columns={abx: 'phenotype'})

    a = ((df[target_gene] == 1) & (df['phenotype'] == 'R')).sum()
    b = ((df[target_gene] == 0) & (df['phenotype'] == 'R')).sum()
    c = ((df[target_gene] == 1) & (df['phenotype'] == 'S')).sum()
    d = ((df[target_gene] == 0) & (df['phenotype'] == 'S')).sum()

    print(abx, a, b, c, d)
    a = 7
    b = 1768
    c = 7
    d = 119

    # 加1平滑
    a += 0.5
    b += 0.5
    c += 0.5
    d += 0.5

    log2_or = np.log2((a / b) / (c / d))

    results.append({
        'antibiotic': abx,
        'log2_OR': log2_or,
    })

df_plot = pd.DataFrame(results).sort_values('log2_OR')
print(df_plot)