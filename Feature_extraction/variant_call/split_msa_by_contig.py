#!/usr/bin/env python3
import os
import sys
from Bio import SeqIO

def safe_filename(name):
    """把 contig 名里的 ';' 替换成 '-'，其他字符保持不变"""
    return name.replace(";", "-")

def split_msa(msa_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for msa_file in sorted(os.listdir(msa_dir)):
        if not msa_file.endswith(".aln.fas"):
            continue

        msa_path = os.path.join(msa_dir, msa_file)
        folder_name = os.path.basename(msa_file).replace(".aln.fas", "")
        folder_path = os.path.join(output_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        records = list(SeqIO.parse(msa_path, "fasta"))
        for record in records:
            contig_name = safe_filename(record.id)
            out_file = os.path.join(folder_path, f"{contig_name}.fa")
            SeqIO.write(record, out_file, "fasta")

        print(f"{msa_file}: split into {len(records)} contig files in {folder_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"用法: {sys.argv[0]} <msa_dir> <output_dir>")
        sys.exit(1)
    split_msa(sys.argv[1], sys.argv[2])