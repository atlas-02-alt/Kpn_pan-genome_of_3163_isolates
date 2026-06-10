#!/usr/bin/env python3
import os
import sys
import re
import shutil
import csv
from Bio import SeqIO

CORE_THRESHOLD = int(3163 * 0.9)

def extract_unique_ids(msa_file):
    unique_ids = set()
    for record in SeqIO.parse(msa_file, "fasta"):
        unique_ids.add(record.id.split(";", 1)[0])
    return unique_ids

def classify_msa(msa_file, output_dir):
    """根据 unique ID 数量分类 MSA 文件"""
    unique_ids = extract_unique_ids(msa_file)
    n_unique = len(unique_ids)

    if n_unique > CORE_THRESHOLD:
        subdir = "core_gene_sequences"
    elif n_unique > 3:
        subdir = "dispensable_gene_sequences"
    else:
        subdir = "rare_gene_sequences"

    out_dir = os.path.join(output_dir, subdir)
    os.makedirs(out_dir, exist_ok=True)

    shutil.copy(msa_file, os.path.join(out_dir, os.path.basename(msa_file)))
    return n_unique, subdir

def main(msa_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    summary_file = os.path.join(output_dir, "pan_gene_classify_summary.tsv")

    with open(summary_file, "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["MSA_file", "Unique_ID_count", "Category"])

        for msa_file in sorted(os.listdir(msa_dir)):
            if not msa_file.endswith(".aln.fas"):
                continue
            msa_path = os.path.join(msa_dir, msa_file)
            n_unique, category = classify_msa(msa_path, output_dir)
            writer.writerow([msa_file, n_unique, category])
            print(f"{msa_file}: {n_unique} unique IDs -> {category}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"用法: {sys.argv[0]} <cleaned_msa_dir> <classified_output_dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])