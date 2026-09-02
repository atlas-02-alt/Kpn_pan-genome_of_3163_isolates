import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import matplotlib as mpl

mpl.rcParams['font.family'] = 'Arial'

def read_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    data = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 2:
            strain, n50 = parts[0], float(parts[1])
            data.append((strain, n50))
    return data
# Read data
data1 = read_data("./figures-trial/fig2-中间文件/Contig_n50_1174.txt")
data2 = read_data("./figures-trial/fig2-中间文件/Contig_n50_491.txt")

# Merge data and add source labels
all_data = [(x[0], x[1], 'Pure short-read assembly') for x in data1] + \
           [(x[0], x[1], 'Hybrid long+short-read assembly') for x in data2]

# Sort by contig N50 in descending order
all_data_sorted = sorted(all_data, key=lambda x: x[1], reverse=True)

# Extract sorted data
n50_values = [x[1] for x in all_data_sorted]
sources = [x[2] for x in all_data_sorted]
x = np.arange(len(all_data_sorted))

# Assign colors by source
color_map = {'Pure short-read assembly': '#91CAE8', 'Hybrid long+short-read assembly': '#F48892'}
colors = [color_map[src] for src in sources]

fig, ax = plt.subplots(figsize=(12,6), dpi=100)

# Set the bar width here; the default is 0.8, and changing it to 0.9 or 1 makes bars wider with smaller gaps
bar_width = 1
bars = ax.bar(x, n50_values, color=colors, width=bar_width)
#bars = ax.bar(x, n50_values, color=colors)

ax.set_xticks([])
ax.set_ylabel('Contig N50')

# Adjust the x-axis range so bars sit closer to the edges, expanding both sides by 0.5 units
ax.set_xlim(-0.5, len(all_data_sorted) - 0.5)

legend_elements = [Patch(facecolor='#91CAE8', label='pure short-read assembly'),
                   Patch(facecolor='#F48892', label='hybrid long+short-read assembly')]
ax.legend(handles=legend_elements, loc='upper right')

plt.tight_layout()
plt.show()
