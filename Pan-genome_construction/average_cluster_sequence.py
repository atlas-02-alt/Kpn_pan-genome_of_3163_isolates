#!/usr/bin/env python3

import os
from collections import Counter
from Bio import SeqIO, AlignIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


msa_dir = "./both-align-results-strict-adv/aligned_gene_sequences/"          # 包含 .fasta 和 .fas 的目录
out_fasta = "./both-align-results-strict-adv/pan_genome_represent.fa"

records_out = []
n_single = 0
n_msa = 0

for fname in sorted(os.listdir(msa_dir)):
    path = os.path.join(msa_dir, fname)

    # ---------- 情况 1：单序列 ----------
    if fname.endswith(".fasta"):
        records = list(SeqIO.parse(path, "fasta"))
        if len(records) != 1:
            continue  # 异常文件，直接跳过

        rec = records[0]
        rec.id = os.path.splitext(fname)[0]
        #rec.description = "single_sequence"
        records_out.append(rec)
        n_single += 1

    # ---------- 情况 2：MSA ----------
    elif fname.endswith(".fas"):
        try:
            alignment = AlignIO.read(path, "fasta")
        except Exception:
            continue

        aln_len = alignment.get_alignment_length()
        consensus = []

        for i in range(aln_len):
            column = alignment[:, i]
            counts = Counter(base for base in column if base not in "-.")

            if counts:
                consensus_base = counts.most_common(1)[0][0]
            else:
                consensus_base = "N"

            consensus.append(consensus_base)

        seq = Seq("".join(consensus))
        cluster_name = (fname.split('.'))[0]

        records_out.append(
            SeqRecord(
                seq,
                id=cluster_name,
                #description="consensus_sequence"
            )
        )
        n_msa += 1


# ---------- 写出 ----------
SeqIO.write(records_out, out_fasta, "fasta")

print(f"[INFO] single-sequence fasta files: {n_single}")
print(f"[INFO] MSA (.fas) files: {n_msa}")
print(f"[INFO] total sequences written: {len(records_out)}")