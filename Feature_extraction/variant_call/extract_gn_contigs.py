#!/usr/bin/env python3
import os
import sys
import shutil
from Bio import SeqIO

TARGET_PATTERN = "GN191724"

def process_msa(msa_file, output_dir, nomatch_dir):
    found = None
    for record in SeqIO.parse(msa_file, "fasta"):
        if TARGET_PATTERN in record.id:
            found = record
            break

    base_name = os.path.basename(msa_file).replace(".aln.fas", "")
    
    if found:
        # 写出 fasta 文件
        os.makedirs(output_dir, exist_ok=True)
        out_file = os.path.join(output_dir, base_name + ".fa")
        # header 使用原 contig 名
        SeqIO.write([found], out_file, "fasta")
        return True
    else:
        # 移动整个 MSA 文件到 nomatch 文件夹
        os.makedirs(nomatch_dir, exist_ok=True)
        shutil.move(msa_file, os.path.join(nomatch_dir, os.path.basename(msa_file)))
        return False

def main(msa_dir, output_dir, nomatch_dir):
    for msa_file in sorted(os.listdir(msa_dir)):
        if not msa_file.endswith(".aln.fas"):
            continue
        msa_path = os.path.join(msa_dir, msa_file)
        found = process_msa(msa_path, output_dir, nomatch_dir)
        if found:
            print(f"{msa_file}: contig extracted")
        else:
            print(f"{msa_file}: no match, moved to {nomatch_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"用法: {sys.argv[0]} <msa_dir> <output_contigs_dir> <no_match_dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
