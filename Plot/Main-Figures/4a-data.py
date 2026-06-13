# 对指定的若干种药物，取特征集（top/full）的并集，然后从FASTA文件中提取对应的序列，输出新的FASTA文件
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple

import pandas as pd


def select_top_features_for_drug(
    df: pd.DataFrame,
    drug: str,
    *,
    drug_col: str = "Antibiotic",
    rank_col: str = "final_rank_by_drug",
    feature_col: str = "Gene",
    top_n: int = 5,
) -> pd.DataFrame:
    sub = df.loc[df[drug_col] == drug].copy()
    if sub.empty:
        return sub

    sub[rank_col] = pd.to_numeric(sub[rank_col], errors="coerce")
    sub = sub.dropna(subset=[rank_col]).sort_values(by=rank_col, kind="stable")
    if sub.empty:
        return sub

    if len(sub) <= top_n:
        return sub

    cutoff_rank = sub.iloc[top_n - 1][rank_col]
    return sub.loc[sub[rank_col] <= cutoff_rank].copy()


def detect_gene_sheet(xlsx_path: str) -> str:
    xls = pd.ExcelFile(xlsx_path)
    gene_sheets = [s for s in xls.sheet_names if "gene" in s.lower()]
    if not gene_sheets:
        raise ValueError(f"No gene-like sheet found. Available sheets: {xls.sheet_names}")
    return gene_sheets[0]


def build_feature_union(
    xlsx_path: str,
    drugs: Sequence[str],
    *,
    mode: str = "top",
    sheet_name: str | None = None,
    drug_col: str = "Antibiotic",
    rank_col: str = "final_rank_by_drug",
    feature_col: str = "Gene",
    top_n: int = 5,
) -> Tuple[List[str], Dict[str, pd.DataFrame]]:
    if sheet_name is None:
        sheet_name = detect_gene_sheet(xlsx_path)
    df = pd.read_excel(xlsx_path, sheet_name=sheet_name)

    required = {drug_col, feature_col}
    if mode == "top":
        required.add(rank_col)
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in sheet '{sheet_name}': {sorted(missing)}")

    union_features: List[str] = []
    seen: Set[str] = set()
    per_drug: Dict[str, pd.DataFrame] = {}

    for drug in drugs:
        if mode == "top":
            selected = select_top_features_for_drug(
                df,
                drug,
                drug_col=drug_col,
                rank_col=rank_col,
                feature_col=feature_col,
                top_n=top_n,
            )
        else:
            selected = df.loc[df[drug_col] == drug].copy()

        per_drug[drug] = selected
        for f in selected[feature_col].dropna().astype(str).tolist():
            if f not in seen:
                seen.add(f)
                union_features.append(f)

    return union_features, per_drug


def normalize_fasta_id(raw_id: str) -> str:
    # Header examples: group_12673_1, pspC_2_1
    # Convert to feature id by removing trailing "_<digits>" only.
    return re.sub(r"_\d+$", "", raw_id)


def extract_sequences_by_features(
    fasta_path: str,
    features: Sequence[str],
) -> Tuple[List[str], Set[str]]:
    feature_set = {str(f) for f in features}
    matched_features: Set[str] = set()
    output_records: List[str] = []

    current_header: str | None = None
    current_seq: List[str] = []

    def flush() -> None:
        nonlocal current_header, current_seq
        if current_header is None:
            return
        seq_id = current_header[1:].strip().split()[0]
        norm_id = normalize_fasta_id(seq_id)
        if norm_id in feature_set:
            output_records.append(current_header + "".join(current_seq))
            matched_features.add(norm_id)
        current_header = None
        current_seq = []

    with open(fasta_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith(">"):
                flush()
                current_header = line if line.endswith("\n") else line + "\n"
            else:
                current_seq.append(line if line.endswith("\n") else line + "\n")
        flush()

    missing_features = feature_set.difference(matched_features)
    return output_records, missing_features


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build feature union (top/all) and extract matched sequences from FASTA."
    )
    parser.add_argument(
        "--xlsx",
        default=r"c:\Users\yxLig\Nutstore\1\我的坚果云 (2)\Klebsiella_pneumoniae\Figures-re\fig5相关数据\supplement\features_analyse.xlsx",
        help="Input feature analysis xlsx path.",
    )
    parser.add_argument(
        "--fasta",
        default=r"c:\Users\yxLig\Nutstore\1\我的坚果云 (2)\Klebsiella_pneumoniae\Figures-re\fig4部分相关数据\supplement\dispensable_genes_17meds_longCentroidID_prot.fa",
        help="Input FASTA path.",
    )
    parser.add_argument(
        "--drugs",
        default="IPM,MEM,ETP",
        help="Comma-separated drug list, e.g. IPM,MEM,ETP",
    )
    parser.add_argument(
        "--mode",
        choices=["top", "all"],
        default="top",
        help="Feature union mode: top=top5-with-ties, all=all features per drug.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Top N for mode=top.",
    )
    parser.add_argument(
        "--out-fa",
        default=None,
        help="Output FASTA path. If omitted, auto-generate in current directory.",
    )
    parser.add_argument(
        "--out-features",
        default=None,
        help="Optional output txt path for union feature list.",
    )
    args = parser.parse_args()

    drugs = [d.strip() for d in args.drugs.split(",") if d.strip()]
    if not drugs:
        raise ValueError("No valid drugs provided.")

    features, _ = build_feature_union(
        args.xlsx,
        drugs,
        mode=args.mode,
        top_n=args.top_n,
    )

    records, missing = extract_sequences_by_features(args.fasta, features)

    if args.out_fa:
        out_fa = Path(args.out_fa)
    else:
        out_fa = Path(f"fig5-{args.mode}-union-extracted.fa")
    out_fa.write_text("".join(records), encoding="utf-8")

    if args.out_features:
        out_features = Path(args.out_features)
        out_features.write_text("\n".join(features) + "\n", encoding="utf-8")

    print(f"Drugs: {drugs}")
    print(f"Mode: {args.mode}")
    print(f"Union feature count: {len(features)}")
    print(f"Extracted fasta record count: {len(records)}")
    print(f"Missing features in fasta: {len(missing)}")
    if missing:
        preview = sorted(list(missing))[:20]
        print(f"Missing preview (up to 20): {preview}")
    print(f"Output fasta: {out_fa.resolve()}")


if __name__ == "__main__":
    main()
