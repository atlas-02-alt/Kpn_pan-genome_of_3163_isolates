from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
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
    fig.savefig(output_path.with_suffix(".pdf"), dpi=300)
    plt.close(fig)

    out_tsv = output_path.with_suffix(".selected.tsv")
    sig.to_csv(out_tsv, sep="\t", index=False)
    print(f"Selected rows: {len(sig)}")
    print(f"Plot saved: {output_path}")
    print(f"Selected table saved: {out_tsv}")


def load_sig_table(input_path: Path, q_cutoff: float) -> pd.DataFrame:
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
        raise ValueError(f"No rows with qvalue < {q_cutoff} in {input_path}.")
    sig["neg_log10_qvalue"] = -np.log10(sig["qvalue"])
    sig = sig.sort_values("qvalue", ascending=True, kind="stable")
    if "GeneRatio" in sig.columns:
        sig["gene_ratio_numeric"] = sig["GeneRatio"].map(parse_gene_ratio)
    else:
        sig["gene_ratio_numeric"] = np.nan
    return sig


def build_stacked_plot(
    input_top: Path,
    input_bottom: Path,
    output_path: Path,
    q_cutoff: float = 0.05,
) -> None:
    top = load_sig_table(input_top, q_cutoff)
    bottom = load_sig_table(input_bottom, q_cutoff)

    cmap = LinearSegmentedColormap.from_list(
        "pheno_harmony_shifted", ["#3A86A8", "#E9C46A", "#D16A5A"]
    )
    fallback_color = "#3A86A8"

    all_ratio = pd.concat(
        [top["gene_ratio_numeric"], bottom["gene_ratio_numeric"]], ignore_index=True
    ).dropna()
    if not all_ratio.empty:
        vmin = float(all_ratio.min())
        vmax = float(all_ratio.max())
        if np.isclose(vmin, vmax):
            norm = plt.Normalize(vmin=vmin - 1e-9, vmax=vmax + 1e-9)
        else:
            norm = plt.Normalize(vmin=vmin, vmax=vmax)
    else:
        norm = None

    top_n = max(1, len(top))
    bot_n = max(1, len(bottom))
    # Keep per-bar visual thickness similar between panels (e.g., 5:2).
    fig_h = 0.85 * (top_n + bot_n) + 2.2
    max_label_len = max(
        [len(str(x)) for x in top["Description"].tolist() + bottom["Description"].tolist()]
    )
    left_margin = min(0.42, max(0.20, 0.0075 * max_label_len + 0.10))

    fig = plt.figure(figsize=(10.2, fig_h))
    gs = gridspec.GridSpec(
        nrows=2,
        ncols=2,
        figure=fig,
        width_ratios=[38, 3.2],
        height_ratios=[top_n, bot_n],
        wspace=0.05,
        hspace=0.42,
    )
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0])
    cax = fig.add_subplot(gs[:, 1])

    def get_colors(sig: pd.DataFrame):
        if norm is not None and sig["gene_ratio_numeric"].notna().any():
            return cmap(norm(sig["gene_ratio_numeric"].fillna(float(all_ratio.min()))))
        return fallback_color

    for ax, sig, title in [
        (ax1, top, f"Core KEGG enrichment (qvalue < {q_cutoff})"),
        (ax2, bottom, f"Dispensable KEGG enrichment (qvalue < {q_cutoff})"),
    ]:
        ax.barh(sig["Description"], sig["neg_log10_qvalue"], color=get_colors(sig))
        ax.set_xlabel("-log10(qvalue)")
        ax.set_ylabel("Pathway")
        ax.set_title(title)
        ax.grid(axis="x", linestyle="--", alpha=0.35)
        ax.invert_yaxis()

    if norm is not None:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(sm, cax=cax)
        cbar.set_label("GeneRatio")
        cbar.ax.tick_params(labelsize=9, pad=2)
    else:
        cax.axis("off")

    # keep figure compact while preserving full pathway labels
    fig.subplots_adjust(left=left_margin, right=0.975, top=0.96, bottom=0.08)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    fig.savefig(output_path.with_suffix(".pdf"), dpi=300)
    plt.close(fig)

    top_out = output_path.with_suffix(".top.selected.tsv")
    bottom_out = output_path.with_suffix(".bottom.selected.tsv")
    top.to_csv(top_out, sep="\t", index=False)
    bottom.to_csv(bottom_out, sep="\t", index=False)
    print(f"Top selected rows: {len(top)}")
    print(f"Bottom selected rows: {len(bottom)}")
    print(f"Plot saved: {output_path}")
    print(f"Top selected table saved: {top_out}")
    print(f"Bottom selected table saved: {bottom_out}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Filter KEGG rows by qvalue and draw a horizontal barplot."
    )
    parser.add_argument(
        "--input",
        default=r"c:\Users\DELL\Desktop\core_dis.list.xls",
        help="Input KEGG table path (tab-delimited text).",
    )
    parser.add_argument(
        "--output",
        default="core_dis-kegg-qvalue-lt0.05-barplot.png",
        help="Output figure path.",
    )
    parser.add_argument(
        "--q-cutoff",
        type=float,
        default=0.05,
        help="qvalue cutoff.",
    )
    parser.add_argument(
        "--input-bottom",
        default=None,
        help="Optional second input table for stacked two-panel plot.",
    )
    args = parser.parse_args()

    if args.input_bottom:
        build_stacked_plot(
            Path(args.input),
            Path(args.input_bottom),
            Path(args.output),
            args.q_cutoff,
        )
    else:
        build_plot(Path(args.input), Path(args.output), args.q_cutoff)


if __name__ == "__main__":
    main()
