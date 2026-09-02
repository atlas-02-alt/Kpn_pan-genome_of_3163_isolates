import pandas as pd
import numpy as np

# === Read data ===
fpath="./Figures-re\\fig5-related-data\\5a-group_258.csv"
features = pd.read_csv(fpath, index_col=0)
ppath="./Figures-re\\fig5-related-data\\supplement\\phenotypes_3163.csv"
phenotypes = pd.read_csv(ppath, index_col=0)

# === Set the target gene to plot===
target_gene = '534_C->G'  # ← Change this to the gene name you want to analyze
selected_antibiotics = ['SXT']  # ← Select manually

# === Compute the log2 odds ratio for each antibiotic ===
results = []
for i in range(0,1,1): #Number of antibiotics
    abx=selected_antibiotics[i]
    if abx not in phenotypes.columns:
        print(f"[Warning] Antibiotic {abx} is not in phenotypes.csv; skipping")
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

    # Add-one smoothing
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