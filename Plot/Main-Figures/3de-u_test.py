import pandas as pd
from scipy import stats

# Read the file
file_path="./Figures-re/fig4-related-data/cd-ablation_cmp - 副本.xlsx"
df = pd.read_excel(file_path,sheet_name='Sheet1')
df = df.iloc[:, 2:]
df.set_index(df.columns[0], inplace=True)

# Exclude NIT when testing known features
df = df[df.index != 'NIT']

# Example: assume the data columns are named 'Column_A' and 'Column_B'
Column_A='test-auc'
Column_B='dis-test-auc'
column_a = df[Column_A]
column_b = df[Column_B]

# **Mann-Whitney U test**：test whether the distributions of two groups differ significantly
# The null hypothesis here is that the two groups come from the same distribution
u_stat, p_value_u = stats.mannwhitneyu(column_a, column_b, alternative='greater')

# Compute variance
var_a = column_a.var(ddof=1)  # Sample variance
var_b = column_b.var(ddof=1)

# Print results
print(f"Mann-Whitney U test statistic:{u_stat}")
print(f"Mann-Whitney U test p-value:{p_value_u}")
if p_value_u < 0.05:
    print("The distributions of the two groups differ significantly")
else:
    print("The distributions of the two groups do not differ significantly")