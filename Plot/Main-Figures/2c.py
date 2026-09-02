import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl

mpl.rcParams['font.family'] = 'Arial'

# 1. Prepare data
data = {
    'Category': ['SNP', 'Insertion', 'Deletion'],
    'Shared': [234930, 192, 215],
    'GN Only': [256998, 728, 1184],
    'GC Only': [163423, 210, 295],
}
df = pd.DataFrame(data).set_index('Category')[['Shared', 'GC Only', 'GN Only']]

# 2. Create the canvas: 1 row and 2 columns with width ratio 1:2; SNP on the left and two Indel panels on the right
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 6), gridspec_kw={'width_ratios': [1, 2]})
colors = ['#464555', '#aba9bc', '#d89b99'] # Bottom to top

# Draw the left panel: SNP with large ticks
df.loc[['SNP']].plot(kind='bar', stacked=True, ax=ax1, color=colors, legend=False, width=0.4)
ax1.set_title('SNP Count', fontsize=12)
ax1.set_ylabel('Number of Variants')
ax1.set_xticklabels(['SNP'], rotation=0)

# Draw the right panel: Insertion and Deletion with small ticks
df.loc[['Insertion', 'Deletion']].plot(kind='bar', stacked=True, ax=ax2, color=colors, width=0.4)
ax2.set_title('Indel Counts', fontsize=12)
ax2.set_xticklabels(['Insertion', 'Deletion'], rotation=0)
ax2.legend(title="Type", loc='upper left')

# Add total-count labels above the bars
for ax, cats in zip([ax1, ax2], [['SNP'], ['Insertion', 'Deletion']]):
    for i, cat in enumerate(cats):
        total = df.loc[cat].sum()
        ax.text(i, total + (total*0.005), f'{total}', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('2e_variant_counts.pdf', format='pdf', bbox_inches='tight')
