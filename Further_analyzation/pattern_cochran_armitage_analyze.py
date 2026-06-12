#!/usr/bin/env python3
"""
Run Cochran-Armitage trend tests for gene-order pattern prevalence.

Input logic:
  - A pattern summary TSV has one row per pattern and a `samples` column.
    Samples in that column are separated by semicolons.
  - The phenotype CSV is used only to define the full sample universe.
    Its first column is assumed to contain sample IDs.
  - HuiNET years are parsed from GN sample IDs, e.g. GN06xxxx -> 2006.
  - Houston years are read from PATRIC_Houston_samples_year.csv.

Outputs:
  1) *_overall_pattern_trend_results.csv
  2) *_overall_pattern_yearly_counts.csv

Example:
  python run_cochran_armitage_patterns.py \
      --collection both \
      --phenotype "phenotypes_3163(1).csv" \
      --huinet-summary HuiNET_pattern_summary.csv \
      --houston-summary Houston_pattern_summary.csv \
      --houston-year PATRIC_Houston_samples_year.csv \
      --outdir results
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
from scipy.stats import norm


def read_phenotype_ids(path: Path) -> List[str]:
    """Read sample IDs from the first column of a phenotype CSV."""
    ids: List[str] = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row and row[0].strip():
                ids.append(row[0].strip())
    return ids


def read_pattern_summary(path: Path) -> List[dict]:
    """Read pattern summary CSV/TSV and parse the semicolon-delimited samples column."""
    rows: List[dict] = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t")
        except csv.Error:
            dialect = csv.excel_tab if path.suffix.lower() == ".tsv" else csv.excel
        reader = csv.DictReader(f, dialect=dialect)
        required = {"abbreviation", "samples"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing required columns: {sorted(missing)}")

        for row in reader:
            raw_samples = row.get("samples", "") or ""
            samples = {x.strip() for x in raw_samples.split(";") if x.strip()}
            rows.append(
                {
                    "abbreviation": (row.get("abbreviation") or "").strip(),
                    "pattern_key": (row.get("pattern_key") or "").strip(),
                    "n_genes": safe_int(row.get("n_genes")),
                    "total_occurrences": safe_int(row.get("total_occurrences"), default=len(samples)),
                    "samples": samples,
                }
            )
    return rows


def safe_int(value, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def build_huinet_sample_year(phenotype_ids: Iterable[str]) -> Dict[str, int]:
    """Parse HuiNET collection year from sample IDs such as GN06xxxx -> 2006."""
    sample_year: Dict[str, int] = {}
    for sid in phenotype_ids:
        if not sid.startswith("GN"):
            continue
        match = re.match(r"^GN(\d{2})", sid)
        if match:
            sample_year[sid] = 2000 + int(match.group(1))
    return sample_year


def read_houston_sample_year(path: Path, phenotype_ids: Iterable[str]) -> Dict[str, int]:
    """Read Houston sample years and keep only IDs present in the phenotype table."""
    phenotype_set = set(phenotype_ids)
    sample_year: Dict[str, int] = {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"Sample_ID", "Collection_Year"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing required columns: {sorted(missing)}")

        for row in reader:
            sid = (row.get("Sample_ID") or "").strip()
            year_raw = (row.get("Collection_Year") or "").strip()
            if sid and year_raw and sid in phenotype_set:
                sample_year[sid] = int(float(year_raw))
    return sample_year


def count_by_year(sample_year: Dict[str, int], positive_samples: set[str]) -> Tuple[List[int], List[int], List[int]]:
    """Return sorted years, positive counts, and total counts."""
    years = sorted(set(sample_year.values()))
    total_by_year = {year: 0 for year in years}
    positive_by_year = {year: 0 for year in years}

    for sid, year in sample_year.items():
        total_by_year[year] += 1
        if sid in positive_samples:
            positive_by_year[year] += 1

    positives = [positive_by_year[y] for y in years]
    totals = [total_by_year[y] for y in years]
    return years, positives, totals


def cochran_armitage_test(years: List[int], positives: List[int], totals: List[int]) -> dict:
    """
    Cochran-Armitage trend test using calendar years as ordered scores.

    Z > 0 means prevalence increases with year.
    Z < 0 means prevalence decreases with year.
    """
    scores = np.asarray(years, dtype=float)
    x = np.asarray(positives, dtype=float)
    n = np.asarray(totals, dtype=float)

    valid = n > 0
    scores = scores[valid]
    x = x[valid]
    n = n[valid]

    total_n = float(n.sum())
    total_x = float(x.sum())
    if len(scores) < 2:
        return {"status": "too_few_years"}
    if total_n <= 0:
        return {"status": "no_samples"}
    if total_x == 0 or total_x == total_n:
        return {"status": "all_zero_or_all_one", "n_years": int(len(scores)), "n_total": int(total_n), "n_positive": int(total_x)}

    p_hat = total_x / total_n
    score_bar = float((n * scores).sum() / total_n)
    numerator = float((scores * (x - n * p_hat)).sum())
    variance = float(p_hat * (1.0 - p_hat) * (n * (scores - score_bar) ** 2).sum())

    if variance <= 0:
        return {"status": "zero_variance"}

    z = numerator / math.sqrt(variance)
    p_two = 2.0 * (1.0 - norm.cdf(abs(z)))

    return {
        "status": "ok",
        "n_years": int(len(scores)),
        "n_total": int(total_n),
        "n_positive": int(total_x),
        "z": z,
        "p_two_sided": p_two,
        "trend_direction": "increasing" if z > 0 else "decreasing" if z < 0 else "flat",
    }


def bh_adjust(p_values: List[float]) -> List[float]:
    """Benjamini-Hochberg adjusted q-values, preserving input order."""
    valid = [(i, p) for i, p in enumerate(p_values) if isinstance(p, (int, float)) and not math.isnan(p)]
    q_values = [math.nan] * len(p_values)
    m = len(valid)
    if m == 0:
        return q_values

    ranked = sorted(valid, key=lambda item: item[1])
    running_min = 1.0
    for reverse_rank, (idx, p) in enumerate(reversed(ranked), start=1):
        rank = m - reverse_rank + 1
        q = min(running_min, p * m / rank)
        running_min = q
        q_values[idx] = min(q, 1.0)
    return q_values


def pattern_sort_key(row: dict) -> Tuple[int, str]:
    match = re.match(r"P(\d+)$", str(row.get("pattern", "")))
    if match:
        return int(match.group(1)), ""
    return 10**9, str(row.get("pattern", ""))


def format_value(value):
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return str(value)
    return value


def write_csv(path: Path, rows: List[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    columns: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in columns:
                columns.append(key)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: format_value(row.get(col, "")) for col in columns})


def p_value_sort(row: dict, p_col: str) -> Tuple[float, Tuple[int, str]]:
    value = row.get(p_col, math.nan)
    try:
        p_value = float(value)
    except Exception:
        p_value = math.nan
    if math.isnan(p_value):
        p_value = math.inf
    return round(p_value, 12), pattern_sort_key(row)


def analyze_collection(collection: str, sample_year: Dict[str, int], summary_rows: List[dict], outdir: Path) -> Tuple[Path, Path]:
    all_samples = set(sample_year)
    results: List[dict] = []
    yearly_rows: List[dict] = []

    if not sample_year:
        raise ValueError(f"No samples with year information for {collection}")

    for row in summary_rows:
        positive_samples = set(row["samples"]) & all_samples
        unmatched_samples = set(row["samples"]) - all_samples
        years, positives, totals = count_by_year(sample_year, positive_samples)
        test = cochran_armitage_test(years, positives, totals)

        total_positive = sum(positives)
        total_samples = sum(totals)
        start_prev = positives[0] / totals[0] if totals[0] else math.nan
        end_prev = positives[-1] / totals[-1] if totals[-1] else math.nan
        overall_prev = total_positive / total_samples if total_samples else math.nan
        prevalences = [pos / total for pos, total in zip(positives, totals) if total]

        result = {
            "collection": collection,
            "pattern": row["abbreviation"],
            "pattern_key": row["pattern_key"],
            "n_genes": row["n_genes"],
            "total_occurrences": row["total_occurrences"],
            "start_year": years[0],
            "end_year": years[-1],
            "n_total": total_samples,
            "n_positive": total_positive,
            "overall_prevalence": overall_prev,
            "start_positive": positives[0],
            "start_total": totals[0],
            "start_prevalence": start_prev,
            "end_positive": positives[-1],
            "end_total": totals[-1],
            "end_prevalence": end_prev,
            "min_prevalence": min(prevalences) if prevalences else math.nan,
            "max_prevalence": max(prevalences) if prevalences else math.nan,
            "unmatched_positive_samples": len(unmatched_samples),
        }
        result.update(test)
        results.append(result)

        for year, pos, total in zip(years, positives, totals):
            if collection == "Houston":
                yearly_row = {
                    "pattern": row["abbreviation"],
                    "pattern_key": row["pattern_key"],
                    "year": year,
                    "pattern_positive": pos,
                    "pattern_negative": total - pos,
                    "total": total,
                    "prevalence": pos / total if total else math.nan,
                }
            else:
                yearly_row = {
                    "pattern": row["abbreviation"],
                    "pattern_key": row["pattern_key"],
                    "year": year,
                    "positive": pos,
                    "negative": total - pos,
                    "total": total,
                    "prevalence": pos / total if total else math.nan,
                }
            yearly_rows.append(yearly_row)

    p_values = [r.get("p_two_sided", math.nan) for r in results]
    for row, q in zip(results, bh_adjust(p_values)):
        row["q_BH_two_sided"] = q

    if collection == "Houston":
        trend_rows = []
        for row in results:
            trend_rows.append(
                {
                    "pattern": row["pattern"],
                    "pattern_key": row["pattern_key"],
                    "n_genes": row["n_genes"],
                    "total_occurrences_all_Houston": row["total_occurrences"],
                    "n_Houston_with_year": row["n_total"],
                    "pattern_positive_with_year": row["n_positive"],
                    "start_year": row["start_year"],
                    "end_year": row["end_year"],
                    "start_positive": row["start_positive"],
                    "start_total": row["start_total"],
                    "start_prevalence": row["start_prevalence"],
                    "end_positive": row["end_positive"],
                    "end_total": row["end_total"],
                    "end_prevalence": row["end_prevalence"],
                    "min_prevalence": row["min_prevalence"],
                    "max_prevalence": row["max_prevalence"],
                    "z_CA": row.get("z", math.nan),
                    "trend_direction_CA": row.get("trend_direction") or "not_tested",
                    "p_two_sided_CA": row.get("p_two_sided", math.nan),
                    "q_BH_p_two_sided_CA": row.get("q_BH_two_sided", math.nan),
                }
            )
        results = sorted(trend_rows, key=lambda r: p_value_sort(r, "p_two_sided_CA"))
    else:
        trend_rows = [
            {
                "pattern": row["pattern"],
                "pattern_key": row["pattern_key"],
                "n_genes": row["n_genes"],
                "total_occurrences": row["total_occurrences"],
                "n_positive_samples_in_HuiNET": row["n_positive"],
                "n_HuiNET_samples": row["n_total"],
                "overall_prevalence": row["overall_prevalence"],
                "start_year": row["start_year"],
                "start_positive": row["start_positive"],
                "start_total": row["start_total"],
                "start_prevalence": row["start_prevalence"],
                "end_year": row["end_year"],
                "end_positive": row["end_positive"],
                "end_total": row["end_total"],
                "end_prevalence": row["end_prevalence"],
                "direction_by_Z": row.get("trend_direction") or "not_tested",
                "CA_Z": row.get("z", math.nan),
                "CA_p_two_sided": row.get("p_two_sided", math.nan),
                "BH_q_two_sided": row.get("q_BH_two_sided", math.nan),
            }
            for row in results
        ]
        results = sorted(trend_rows, key=pattern_sort_key)

    yearly_rows = sorted(yearly_rows, key=lambda r: (pattern_sort_key(r), r["year"]))

    outdir.mkdir(parents=True, exist_ok=True)
    result_path = outdir / f"{collection}_overall_pattern_trend_results.csv"
    yearly_path = outdir / f"{collection}_overall_pattern_yearly_counts.csv"
    write_csv(result_path, results)
    write_csv(yearly_path, yearly_rows)
    return result_path, yearly_path


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Cochran-Armitage trend tests for pattern prevalence.")
    parser.add_argument("--collection", choices=["huinet", "houston", "both"], default="both")
    parser.add_argument("--phenotype", type=Path, default=Path("phenotypes_3163(1).csv"))
    parser.add_argument("--huinet-summary", type=Path, default=Path("HuiNET_pattern_summary.tsv"))
    parser.add_argument("--houston-summary", type=Path, default=Path("Houston_pattern_summary.tsv"))
    parser.add_argument("--houston-year", type=Path, default=Path("PATRIC_Houston_samples_year.csv"))
    parser.add_argument("--outdir", type=Path, default=script_dir)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    phenotype_ids = read_phenotype_ids(args.phenotype)
    written: List[Path] = []

    if args.collection in {"huinet", "both"}:
        huinet_sample_year = build_huinet_sample_year(phenotype_ids)
        huinet_rows = read_pattern_summary(args.huinet_summary)
        written.extend(analyze_collection("HuiNET", huinet_sample_year, huinet_rows, args.outdir))
        print(f"HuiNET samples with year: {len(huinet_sample_year)}")

    if args.collection in {"houston", "both"}:
        houston_sample_year = read_houston_sample_year(args.houston_year, phenotype_ids)
        houston_rows = read_pattern_summary(args.houston_summary)
        written.extend(analyze_collection("Houston", houston_sample_year, houston_rows, args.outdir))
        print(f"Houston samples with year: {len(houston_sample_year)}")

    print("Wrote:")
    for path in written:
        print(f"  {path}")


if __name__ == "__main__":
    main()
