import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['font.family'] = 'Arial'

# Raw variant data
data = {
    'synonymous_variant': 439892,
    'missense_variant': 211767,
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

# Category statistics
synonymous = data.get('synonymous_variant', 0)
missense = data.get('missense_variant', 0)
other = sum(count for k, count in data.items()
            if k != 'synonymous_variant' and k != 'missense_variant')

# Prepare plotting data
labels = ['Synonymous', 'Missense', 'Other']
sizes = [synonymous, missense, other]
colors = ['#b4d7e5', '#bedeab',  '#A8A6D3']
print(sizes) # Output is[439892, 211767, 8848]

# Draw the pie chart
plt.figure(figsize=(8, 8))
plt.pie(
    sizes, labels=None, autopct=None,
    colors=colors, startangle=140)

plt.title('Variant Classification Pie Chart', fontsize=16)
plt.axis('equal')  # Ensure the pie chart is circular
plt.show()
