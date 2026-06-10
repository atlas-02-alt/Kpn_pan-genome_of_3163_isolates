#!/usr/bin/env python3
import os
import sys
from collections import Counter
from Bio import SeqIO

def get_mode_length(lengths):
    """计算众数长度"""
    counter = Counter(lengths)
    return counter.most_common(1)[0][0]

def clean_msa(msa_file, output_file):
    """去掉异常序列并写入新文件"""
    records = list(SeqIO.parse(msa_file, "fasta"))
    if not records:
        return 0, 0

    lengths = [len(r.seq) for r in records]
    mode_length = get_mode_length(lengths)

    lower = mode_length * 0.8
    upper = mode_length * 1.2

    cleaned_records = [r for r in records if lower <= len(r.seq) <= upper]

    # 写回 fasta 文件，保持格式
    SeqIO.write(cleaned_records, output_file, "fasta")

    removed = len(records) - len(cleaned_records)
    return len(records), removed

def main(msa_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for msa_file in sorted(os.listdir(msa_dir)):
        if not msa_file.endswith(".aln.fas"):
            continue

        msa_path = os.path.join(msa_dir, msa_file)
        out_path = os.path.join(output_dir, msa_file)

        total, removed = clean_msa(msa_path, out_path)
        print(f"{msa_file}: total={total}, removed={removed}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"用法: {sys.argv[0]} <msa_dir> <output_dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])