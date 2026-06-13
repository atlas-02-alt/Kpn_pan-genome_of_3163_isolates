from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

# 17 antibiotics
MEDS = [
    "CZO",
    "FOX",
    "CXM",
    "CAZ",
    "ETP",
    "IPM",
    "MEM",
    "SAM",
    "TZP",
    "GEN",
    "AMK",
    "TOB",
    "TCY",
    "CIP",
    "LVX",
    "NIT",
    "SXT",
]

# ---------- You only need to edit these paths ----------
MODEL_PATH_TEMPLATE: Path | None = Path(
    "/data/home/sfwang/kpn/Panaroo-DownStream-both/feature_set_determine/5f_avgauc_train/result/{med}/best_model.pkl"
)
MODEL_PATH_BY_MED: Dict[str, Path] = {}

# Test/Validation CSV path templates. Each CSV must include one "label" column.
TEST_PATH_TEMPLATE: Path | None = Path(
    "/data/home/sfwang/kpn/Panaroo-DownStream-both/feature_set_determine/5f_avgauc_test/result_test_matrix/{med}.csv"
)
VALIDATION_PATH_TEMPLATE: Path | None = Path(
    "/data/home/sfwang/kpn/Panaroo-DownStream-both/feature_set_determine/5f_avgauc_test/result_validation_matrix/{med}.csv"
)
TEST_PATH_BY_MED: Dict[str, Path] = {}
VALIDATION_PATH_BY_MED: Dict[str, Path] = {}

OUTPUT_DIR = Path("./permutation_importance_on_test")

SCORING = "roc_auc"
N_REPEATS = 30
RANDOM_STATE = 42
N_JOBS = -1
NORMALIZE = True
TOP_N = 5
# -------------------------------------------------------


def resolve_med_path(
    med: str,
    *,
    path_template: Path | None,
    path_by_med: Dict[str, Path] | None = None,
) -> Path | None:
    if path_by_med and med in path_by_med:
        return Path(path_by_med[med])
    if path_template is None:
        return None
    return Path(str(path_template).format(med=med))


def _read_matrix_with_label(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, index_col=0)
    if "label" not in df.columns:
        raise ValueError(f"'{csv_path}' has no 'label' column.")
    return df


def load_xy_from_concat_csvs(
    test_csv_path: Path, validation_csv_path: Path
) -> tuple[pd.DataFrame, pd.Series]:
    test_df = _read_matrix_with_label(test_csv_path)
    validation_df = _read_matrix_with_label(validation_csv_path)

    # Row-wise concat with aligned columns.
    df = pd.concat([test_df, validation_df], axis=0, join="outer", sort=False)

    y = pd.to_numeric(df["label"], errors="coerce")
    valid_mask = y.notna()
    if not valid_mask.all():
        dropped = int((~valid_mask).sum())
        print(
            f"[warn] {test_csv_path.name}+{validation_csv_path.name}: "
            f"drop {dropped} rows due to invalid label."
        )

    df = df.loc[valid_mask].copy()
    y = y.loc[valid_mask].astype(int)
    X = df.drop(columns=["label"])

    X = X.apply(pd.to_numeric, errors="coerce").fillna(0)
    return X, y


def align_X_to_model_features(X: pd.DataFrame, model: object) -> pd.DataFrame:
    expected = getattr(model, "feature_names_in_", None)
    if expected is None:
        return X

    expected = list(expected)
    miss = [c for c in expected if c not in X.columns]
    if miss:
        raise ValueError(f"Missing columns required by model: {miss[:10]}")
    return X.loc[:, expected]


def compute_soft_voting_importance(
    voting_model: object,
    X: pd.DataFrame,
    y: pd.Series,
    feature_names: List[str] | None = None,
    scoring: str = "roc_auc",
    n_repeats: int = 30,
    random_state: int = 42,
    n_jobs: int = -1,
    normalize: bool = True,
) -> pd.DataFrame:
    result = permutation_importance(
        voting_model,
        X,
        y,
        scoring=scoring,
        n_repeats=n_repeats,
        random_state=random_state,
        n_jobs=n_jobs,
    )

    importances_mean = result.importances_mean
    importances_std = result.importances_std

    if normalize:
        total = np.sum(np.abs(importances_mean))
        if total != 0:
            importances_mean = importances_mean / total

    if feature_names is None:
        feature_names = list(X.columns)

    df = pd.DataFrame(
        {
            "feature": feature_names,
            "importance_mean": importances_mean,
            "importance_std": importances_std,
            "abs_importance": np.abs(importances_mean),
        }
    )
    df = df.sort_values(by="abs_importance", ascending=False, kind="stable").reset_index(
        drop=True
    )
    return df


def run_single_med(med: str) -> pd.DataFrame:
    model_path = resolve_med_path(
        med,
        path_template=MODEL_PATH_TEMPLATE,
        path_by_med=MODEL_PATH_BY_MED,
    )
    test_path = resolve_med_path(
        med,
        path_template=TEST_PATH_TEMPLATE,
        path_by_med=TEST_PATH_BY_MED,
    )
    valid_path = resolve_med_path(
        med,
        path_template=VALIDATION_PATH_TEMPLATE,
        path_by_med=VALIDATION_PATH_BY_MED,
    )

    if model_path is None:
        raise ValueError("MODEL_PATH_TEMPLATE/MODEL_PATH_BY_MED is not configured.")
    if test_path is None:
        raise ValueError("TEST_PATH_TEMPLATE/TEST_PATH_BY_MED is not configured.")
    if valid_path is None:
        raise ValueError(
            "VALIDATION_PATH_TEMPLATE/VALIDATION_PATH_BY_MED is not configured."
        )
    if not model_path.exists():
        raise FileNotFoundError(f"model file not found: {model_path}")
    if not test_path.exists():
        raise FileNotFoundError(f"test csv not found: {test_path}")
    if not valid_path.exists():
        raise FileNotFoundError(f"validation csv not found: {valid_path}")

    model = joblib.load(model_path)
    X, y = load_xy_from_concat_csvs(test_path, valid_path)
    X = align_X_to_model_features(X, model)

    out_df = compute_soft_voting_importance(
        voting_model=model,
        X=X,
        y=y,
        feature_names=list(X.columns),
        scoring=SCORING,
        n_repeats=N_REPEATS,
        random_state=RANDOM_STATE,
        n_jobs=N_JOBS,
        normalize=NORMALIZE,
    )
    out_df.insert(0, "med", med)
    return out_df


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_rows: List[pd.DataFrame] = []

    for med in MEDS:
        try:
            result_df = run_single_med(med)
        except Exception as e:
            print(f"[{med}] failed: {e}")
            continue

        out_path = OUTPUT_DIR / f"{med}_permutation_importance.csv"
        result_df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"[{med}] saved -> {out_path}")

        top_df = result_df.head(TOP_N).copy()
        summary_rows.append(top_df)

    if summary_rows:
        summary_df = pd.concat(summary_rows, axis=0, ignore_index=True)
        summary_path = OUTPUT_DIR / f"top{TOP_N}_summary.csv"
        summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
        print(f"[summary] saved -> {summary_path}")
    else:
        print("[summary] no result generated.")


if __name__ == "__main__":
    main()
