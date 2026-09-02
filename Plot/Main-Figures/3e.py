import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from statannotations.Annotator import Annotator

# Read the file
file_path = "./Figures-re/fig4-related-data/cd-ablation_cmp.xlsx"
df = pd.read_excel(file_path,sheet_name='Sheet1')
columns_to_plot = ['test-auc', 'known-test-auc', 'validation-auc', 'known-vali-auc']
df = df.iloc[:, 2:]
df.set_index(df.columns[0], inplace=True)
df = df[columns_to_plot]
df = df.rename(columns={'test-auc': "test-Total",
                        'known-test-auc': "test-Known",
                        'validation-auc': "validate-Total",
                        'known-vali-auc': "validate-Known"})
print(df.shape)

# Customize the color of each boxplot
box_colors = ['#7db3c6', '#ddc4e2', '#7db3c6', '#ddc4e2']

# Draw the boxplot
plt.figure(figsize=(8.3, 6))
sns.boxplot(data=df, palette=box_colors, showfliers=False, width=0.45)

# Show each data point using solid black dots
sns.stripplot(data=df, color='black', jitter=False, size=4, alpha=0.6)

# Connect the two test columns and the two validation columns
for i in range(len(df)):
    # Connect test-Total and test-Known
    plt.plot([0, 1], [df.iloc[i, 0], df.iloc[i, 1]], color='gray', linewidth=0.5, alpha=0.3, zorder=0)
    # Connect validate-Total and validate-Known
    plt.plot([2, 3], [df.iloc[i, 2], df.iloc[i, 3]], color='gray', linewidth=0.5, alpha=0.3, zorder=0)

# Show the figure
plt.ylim(0.3, 1.1)
plt.show()
