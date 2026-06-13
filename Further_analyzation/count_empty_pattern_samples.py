import argparse
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


DEFAULT_TARGET_GENES = [
    "group_7560",
    "group_12673",
    "group_2412",
    "bla_3~~~bla_1~~~bla_2~~~bla_6",
    "bla_7~~~bla_6~~~bla_3~~~bla_4",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Count sample columns where all target-gene rows are empty in a CSV matrix."
        )
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to the CSV file. The first column is read as row index.",
    )
    parser.add_argument(
        "--target-genes",
        default=",".join(DEFAULT_TARGET_GENES),
        help=(
            "Comma-separated row names to extract from the CSV index. "
            "Default: %(default)s"
        ),
    )
    parser.add_argument(
        "--gff-dir",
        default=None,
        help=(
            "Optional directory containing sample GFF/GFF3 files. When "
            "--sample-start-col is not set, this is used only to infer the "
            "first sample column, matching the fig4fgh/fig5efg behavior."
        ),
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help=(
            "Optional output directory. If set, a per-sample status TSV is "
            "written there unless --out is provided."
        ),
    )
    parser.add_argument(
        "--sample-start-col",
        default=None,
        help=(
            "First sample column name, or 0-based column index after reading the CSV "
            "index. Columns before this are treated as annotations and skipped. "
            "Default: use all columns after reading the CSV index."
        ),
    )
    parser.add_argument(
        "--check-sample",
        default="GN191724",
        help="Sample column to report separately. Default: %(default)s",
    )
    parser.add_argument(
        "--out",
        default=None,
        help=(
            "Optional output TSV path for per-sample empty/non-empty status. "
            "Default: do not write a table."
        ),
    )
    return parser.parse_args()


def parse_target_genes(target_genes_text: str) -> List[str]:
    genes = [g.strip() for g in target_genes_text.split(",") if g.strip()]
    if not genes:
        raise ValueError("--target-genes did not contain any row names.")
    return genes


def resolve_target_index_rows(index_values: List[str], target_genes: List[str]) -> Dict[str, str]:
    target_to_index: Dict[str, str] = {}
    for target in target_genes:
        exact_matches = [idx for idx in index_values if idx == target]
        if exact_matches:
            target_to_index[target] = exact_matches[0]
            continue

        prefix_matches = [idx for idx in index_values if idx.startswith(target)]
        if len(prefix_matches) == 1:
            target_to_index[target] = prefix_matches[0]
        elif len(prefix_matches) > 1:
            raise ValueError(
                f"Target row prefix {target!r} matched multiple CSV index rows: "
                f"{prefix_matches}"
            )
        else:
            raise ValueError(
                f"CSV index is missing target row name/prefix: {target!r}"
            )
    return target_to_index


def build_sample_gff_map(gff_dir: Path, samples: List[str]) -> Dict[str, Path]:
    gff_files = list(gff_dir.rglob("*.gff")) + list(gff_dir.rglob("*.gff3"))
    sample_to_path: Dict[str, Path] = {}
    lowered = [(p, p.name.lower(), p.stem.lower()) for p in gff_files]

    for sample in samples:
        token = sample.lower()
        hits = []
        for p, lname, lstem in lowered:
            if token in lname or token == lstem:
                hits.append(p)
        if len(hits) == 1:
            sample_to_path[sample] = hits[0]
        elif len(hits) > 1:
            exact = [p for p in hits if p.stem.lower() == token]
            if len(exact) == 1:
                sample_to_path[sample] = exact[0]
    return sample_to_path


def infer_sample_columns(
    all_columns: List[str], sample_start_col: Optional[str], gff_dir: Optional[Path]
) -> List[str]:
    if not all_columns:
        raise ValueError("No columns found in the CSV after reading the first column as index.")

    if sample_start_col is None:
        if gff_dir is not None:
            for idx, col in enumerate(all_columns):
                if build_sample_gff_map(gff_dir, [col]):
                    return all_columns[idx:]
        return all_columns

    token = str(sample_start_col).strip()
    if token in all_columns:
        start_idx = all_columns.index(token)
    else:
        try:
            start_idx = int(token)
        except ValueError as exc:
            raise ValueError(
                f"--sample-start-col must be an existing column name or a 0-based "
                f"column index, got: {sample_start_col}"
            ) from exc
        if start_idx < 0 or start_idx >= len(all_columns):
            raise ValueError(
                f"--sample-start-col index {start_idx} is out of range for "
                f"{len(all_columns)} CSV columns."
            )
    return all_columns[start_idx:]


def is_empty_cell(value: object) -> bool:
    if pd.isna(value):
        return True
    text = str(value).strip()
    return text == "" or text.lower() in {"nan", "na", "none", "null"}


def main() -> None:
    args = parse_args()
    csv_path = Path(args.csv)
    gff_dir = Path(args.gff_dir) if args.gff_dir else None

    raw_df = pd.read_csv(csv_path, index_col=0)
    raw_df.index = raw_df.index.astype(str)

    target_genes = parse_target_genes(args.target_genes)
    target_to_index = resolve_target_index_rows(raw_df.index.tolist(), target_genes)

    all_value_cols = [str(c) for c in raw_df.columns]
    raw_df.columns = all_value_cols
    sample_cols = infer_sample_columns(all_value_cols, args.sample_start_col, gff_dir)
    if not sample_cols:
        raise ValueError("No sample columns found.")

    matched_index_rows = [target_to_index[g] for g in target_genes]
    target_df = raw_df.loc[matched_index_rows, sample_cols].copy()
    target_df.index = target_genes

    result_rows = []
    all_empty_samples = []
    for sample in sample_cols:
        values = target_df[sample].tolist()
        empty_flags = [is_empty_cell(v) for v in values]
        all_empty = all(empty_flags)
        if all_empty:
            all_empty_samples.append(sample)
        result_rows.append(
            {
                "sample": sample,
                "all_target_genes_empty": all_empty,
                "n_empty_target_genes": sum(empty_flags),
                "n_target_genes": len(target_genes),
            }
        )

    result_df = pd.DataFrame(result_rows)
    check_sample = str(args.check_sample)
    check_row = result_df.loc[result_df["sample"] == check_sample]

    print(f"CSV: {csv_path}")
    print(f"Selected target rows: {len(target_genes)}")
    print(f"Sample columns: {len(sample_cols)}")
    print(f"All-empty target-gene samples: {len(all_empty_samples)}")
    print(
        "All-empty target-gene samples starting with GN: "
        f"{sum(sample.startswith('GN') for sample in all_empty_samples)}"
    )

    if check_row.empty:
        print(f"{check_sample}: sample column not found")
    else:
        check_is_empty = bool(check_row.iloc[0]["all_target_genes_empty"])
        print(f"{check_sample} all target genes empty: {check_is_empty}")

    out_path = None
    if args.out:
        out_path = Path(args.out)
    elif args.out_dir:
        out_path = Path(args.out_dir) / "fig4e_target_empty_sample_status.tsv"

    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        result_df.to_csv(out_path, sep="\t", index=False)
        print(f"Per-sample status written to: {out_path}")


if __name__ == "__main__":
    main()
