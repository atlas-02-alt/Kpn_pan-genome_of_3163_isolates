import glob
import gzip
from collections import Counter

def parse_ann_field(info_field):
    for entry in info_field.split(';'):
        if entry.startswith('ANN='):
            ann_field = entry[len('ANN='):]
            annotations = ann_field.split(',')
            for ann in annotations:
                fields = ann.split('|')
                if len(fields) > 1:
                    yield fields[1]  

variant_counter = Counter()

vcf_files = glob.glob("./both-align-results-strict-adv/ann_vcf/*.vcf")

for file in vcf_files:
    open_func = gzip.open if file.endswith(".gz") else open
    with open_func(file, 'rt') as f:
        for line in f:
            if line.startswith("#"):
                continue
            cols = line.strip().split('\t')
            info = cols[7]
            for effect in parse_ann_field(info):
                variant_counter[effect] += 1

for effect, count in variant_counter.most_common():
    print(f"{effect}: {count}")
