import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

mpl.rcParams['font.family'] = 'Arial'

# Raw variant data
data = {
    'upstream_gene_variant': 2034,
    'intergenic_region': 1895,
    'stop_gained': 1138,
    'disruptive_inframe_deletion': 848,
    'disruptive_inframe_insertion': 621,
    'frameshift_variant': 520,
    'splice_region_variant&stop_retained_variant': 506,
    'conservative_inframe_deletion': 490,
    'conservative_inframe_insertion': 332,
    'downstream_gene_variant': 296,
    'start_lost': 115,
    'initiator_codon_variant': 29,
    'stop_lost&splice_region_variant': 17,
    'frameshift_variant&stop_gained': 4,
    'start_retained_variant': 2,
    'frameshift_variant&stop_lost&splice_region_variant': 1
}

categories = [key for key in data]
values = [data[key] for key in data]

plt.figure(figsize=(10, 7))
bars = plt.bar(categories, values, color='gray')

# Rotate x-axis labels by 45 degrees
plt.xticks(rotation=45, ha='right', fontsize=11)

# Show raw values above the bars instead of log values
for i, bar in enumerate(bars):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
             f'{values[i]:,}', ha='center', va='bottom', fontsize=10)

plt.title("")
plt.ylabel("count")
plt.xlabel("variant type")
plt.tight_layout()
plt.show()
