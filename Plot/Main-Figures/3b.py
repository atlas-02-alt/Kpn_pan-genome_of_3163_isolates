import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# Global font settings
mpl.rcParams.update({
    'font.family': 'Arial',            # Force Arial
    'axes.unicode_minus': False,       # Fix garbled minus signs
    'pdf.fonttype': 42, 'ps.fonttype': 42
})

# Read data
path = "./Figures-re/fig4-related-data/a-candidates_distribution.xlsx"
df = pd.read_excel(path, sheet_name='med', index_col=0)

# Select two columns; this assumes the first two columns and can be modified as needed
selected_columns = df.columns[0:2]  # Modify this to select the columns you need
df_selected = df[selected_columns]

# Manually specify the color list for each row as needed
row_colors = ['#377EB8', '#377EB8', '#377EB8', '#377EB8', '#B23648', '#B23648', '#B23648', '#DC7369', '#DC7369',
              '#D8EBCD', '#D8EBCD', '#D8EBCD', '#F8EFB5', '#DAD4B9', '#DAD4B9', '#C8CDCF', '#E1F3FA']
#row_colors = ['#377EB8', '#B23648', '#DC7369', '#D8EBCD', '#F8EFB5', '#DAD4B9', '#C8CDCF', '#E1F3FA']

# Set hatch styles
hatch_styles = ['', '/']  # Some common hatch patterns

# Generate two legend handles separately
legend_elements = [
    plt.Rectangle((0,0),1,1, facecolor='white', edgecolor='black', hatch='/', label='unknown'),
    plt.Rectangle((0,0),1,1, facecolor='white', edgecolor='black', hatch='', label='known')
]

# Plot
fig, ax = plt.subplots(figsize=(4, 6.3))
bottom = [0] * len(df_selected)
y_pos = range(len(df_selected))  # y-axis position

# Stacked plotting
for idx, drug_class in enumerate(df_selected.columns):
    ax.barh(
        y=y_pos,
        width=df_selected[drug_class],
        left=bottom,
        height=0.8,
        color=row_colors,  # Use specified colors for each row
        hatch=hatch_styles[idx % len(hatch_styles)],  # Cycle hatch patterns by column index
        edgecolor='black'  # Add edge color
    )
    bottom = [i + j for i, j in zip(bottom, df_selected[drug_class])]

# Set y-axis labels
ax.set_yticks(y_pos)
ax.set_yticklabels(df_selected.index)

# Key adjustment: set top and bottom margins to half a bar height
ax.set_ylim(-0.65, len(df_selected) - 0.35)

# Create a custom legend showing hatch styles only
# Generate two legend handles separately
legend_elements = [
    plt.Rectangle((0,0),1,1, facecolor='white', edgecolor='black', hatch='', label='known'),
    plt.Rectangle((0,0),1,1, facecolor='white', edgecolor='black', hatch='/', label='unknown')
]

#ax.legend(handles=legend_elements, loc='upper right')

# Labels and legend
ax.set_xlabel("selected candidates")
ax.set_title("v-features distribution")

ax.invert_yaxis()
plt.tight_layout()
plt.show()