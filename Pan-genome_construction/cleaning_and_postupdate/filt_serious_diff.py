#!/usr/bin/env python3
import sys
import pandas as pd

def filter_serious_discrepancies(input_file, output_file):
    # 读取表格
    df = pd.read_csv(input_file, sep="\t")

    # 转换为数值（NA 保持为 NaN）
    df["Reference_length"] = pd.to_numeric(df["Reference_length"], errors="coerce")
    df["Mode_length"] = pd.to_numeric(df["Mode_length"], errors="coerce")

    # 计算差值
    df["Abs_diff"] = (df["Mode_length"] - df["Reference_length"]).abs()
    df["Rel_diff"] = df["Abs_diff"] / df["Reference_length"]

    # 筛选差距严重的条目：>100bp 且 >20%
    serious = df[(df["Abs_diff"] > 100) & (df["Rel_diff"] > 0.2)]

    # 保存结果
    serious.to_csv(output_file, sep="\t", index=False)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"用法: {sys.argv[0]} <msa_length_summary.tsv> <serious_diff.tsv>")
        sys.exit(1)
    filter_serious_discrepancies(sys.argv[1], sys.argv[2])
