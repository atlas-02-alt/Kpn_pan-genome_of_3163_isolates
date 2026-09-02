from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap


def parse_gene_ratio(value: object) -> float:
    if pd.isna(value):
        return np.nan
    text = str(value).strip()
    if "/" in text:
        left, right = text.split("/", 1)
        try:
            denom = float(right)
            if denom == 0:
                return np.nan
            return float(left) / denom
        except ValueError:
            return np.nan
    try:
        return float(text)
    except ValueError:
        return np.nan


def build_plot(input_path: Path, output_path: Path, q_cutoff: float = 0.05) -> None:
    plt.rcParams["font.family"] = "Arial"

    # This file is tab-delimited text with a .xls suffix.
    df = pd.read_csv(input_path, sep="\t")

    if "qvalue" not in df.columns:
        raise ValueError(f"Column 'qvalue' not found. Columns: {list(df.columns)}")
    if "Description" not in df.columns:
        raise ValueError(f"Column 'Description' not found. Columns: {list(df.columns)}")

    df["qvalue"] = pd.to_numeric(df["qvalue"], errors="coerce")
    selected_cols = ["Description", "qvalue"]
    if "GeneRatio" in df.columns:
        selected_cols.append("GeneRatio")
    sig = df.loc[df["qvalue"] < q_cutoff, selected_cols].dropna(subset=["Description", "qvalue"]).copy()
    if sig.empty:
        raise ValueError(f"No rows with qvalue < {q_cutoff}.")

    sig["neg_log10_qvalue"] = -np.log10(sig["qvalue"])
    sig = sig.sort_values("qvalue", ascending=True, kind="stable")
    if "GeneRatio" in sig.columns:
        sig["gene_ratio_numeric"] = sig["GeneRatio"].map(parse_gene_ratio)
    else:
        sig["gene_ratio_numeric"] = np.nan

    if sig["gene_ratio_numeric"].notna().any():
        vmin = float(sig["gene_ratio_numeric"].min())
        vmax = float(sig["gene_ratio_numeric"].max())
        if np.isclose(vmin, vmax):
            norm = plt.Normalize(vmin=vmin - 1e-9, vmax=vmax + 1e-9)
        else:
            norm = plt.Normalize(vmin=vmin, vmax=vmax)
        cmap = LinearSegmentedColormap.from_list(
            "pheno_harmony_shifted", ["#3A86A8", "#E9C46A", "#D16A5A"]
        )
        bar_colors = cmap(norm(sig["gene_ratio_numeric"].fillna(vmin)))
    else:
        norm = None
        cmap = None
        bar_colors = "#3A86A8"

    height = max(4, 0.42 * len(sig) + 1.2)
    fig, ax = plt.subplots(figsize=(11, height))
    ax.barh(sig["Description"], sig["neg_log10_qvalue"], color=bar_colors)
    ax.set_xlabel("-log10(qvalue)")
    ax.set_ylabel("Pathway")
    ax.set_title(f"KEGG enrichment (qvalue < {q_cutoff})")
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    ax.invert_yaxis()
    if norm is not None and cmap is not None:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, pad=0.02)
        cbar.set_label("GeneRatio")
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path = output_path.with_suffix(".pdf")
    fig.savefig(pdf_path, dpi=300)
    plt.close(fig)
    print(f"Selected rows: {len(sig)}")
    print(f"Plot saved: {pdf_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Filter KEGG rows by qvalue and draw a horizontal barplot."
    )
    parser.add_argument(
        "--input",
        default=r"./core_dis.list.xls",
        help="Input KEGG table path (tab-delimited text).",
    )
    parser.add_argument(
        "--output",
        default="kegg-qvalue-lt0.05-barplot.pdf",
        help="Output figure path (PDF).",
    )
    parser.add_argument(
        "--q-cutoff",
        type=float,
        default=0.05,
        help="qvalue cutoff.",
    )
    args = parser.parse_args()
    build_plot(Path(args.input), Path(args.output), args.q_cutoff)


if __name__ == "__main__":
    main()
