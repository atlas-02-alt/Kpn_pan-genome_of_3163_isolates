import matplotlib.pyplot as plt
import scipy.stats as stats
import matplotlib as mpl

mpl.rcParams['font.family'] = 'Arial'

INPUT_FILE = "./figures-new/fig2-中间文件/anhui_sample_gene_counts.txt"
OUTPUT_FILE = "gene_count_trapezoid_plot.pdf"

def read_data(filename):
    # Return a dictionary with sample names as keys and N50 values as values
    with open(filename, 'r') as f:
        lines = f.readlines()
    data = {}
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 2:
            strain, n50 = parts[0], float(parts[1])
            data[strain]=n50
    return data

data1 = read_data("./figures-new/fig2-中间文件/anhui_contig_n50_1174.txt")
data2 = read_data("./figures-new/fig2-中间文件/anhui_contig_n50_491.txt")

# Read and sort
data = []
with open(INPUT_FILE) as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        sample, count = parts
        if sample in data1:
            try:
                data.append((sample, int(count),'Pure short-read',data1[sample]))
            except ValueError:
                continue
        elif sample in data2:
            try:
                data.append((sample, int(count),'Hybrid long+short-read',data2[sample]))
            except ValueError:
                continue

data_sorted = sorted(data, key=lambda x: x[3], reverse=True)

# Extract sorted data
gene_count_1174 = [x[1] for x in data_sorted if x[2]=='Pure short-read']
gene_count_491 = [x[1] for x in data_sorted if x[2]=='Hybrid long+short-read']
print(len(gene_count_1174), len(gene_count_491))

import seaborn as sns
import pandas as pd
df = pd.DataFrame({
    'Value': gene_count_1174 + gene_count_491,  # Merge data from the two lists
    'List': ['Pure short-read'] * len(gene_count_1174) + ['Hybrid long+short-read'] * len(gene_count_491)  # Mark the data source
})

# Compute the p-value of the Wilcoxon rank-sum (Mann-Whitney U) test
u_stat, p_value = stats.mannwhitneyu(gene_count_491, gene_count_1174, alternative='greater')
print(f'Mann-Whitney U Statistic: {u_stat}')
print(f'Wilcoxon rank-sum test p-value: {p_value}')

# Create the figure
plt.figure(figsize=(4, 6))

# Use seaborn to draw the boxplot
sns.boxplot(x='List',
            y='Value',
            data=df,
            palette=["#91CAE8", "#F48892"],
            width=0.4,  # Set box width
            flierprops=dict(marker='o', color='r', markersize=5, markeredgewidth=1))  # Set scatter-point style

# Set the y-axis upper limit
plt.ylim(4500, 7500)

# Set title and labels
plt.title('Gene Numbers from Two Assembly Methods', fontsize=12)
plt.xlabel('Assembly Method', fontsize=10)
plt.ylabel('Gene Number', fontsize=10)

# Show the figure
plt.tight_layout()
plt.show()