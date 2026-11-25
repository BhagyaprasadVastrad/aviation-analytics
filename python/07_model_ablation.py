"""Feature ablation and lead-time comparison for the delay model (gradient boosting only).

Answers two questions:
  1. How much of the predictive power comes from each feature group?
  2. How does accuracy change if the prediction is made 60, 120 or 180 minutes before departure?

Usage:
    python python/07_model_ablation.py
    python python/07_model_ablation.py --parquet data/processed/flights_clean.parquet

Output: documentation/ablation_results.md
"""
import argparse
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

ROOT = Path(__file__).resolve().parents[1]

# Reuse the feature building, split and metrics from the main model script
_spec = importlib.util.spec_from_file_location("delay_model", ROOT / "python" / "05_delay_model.py")
dm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dm)

CATS = ["airline_code", "origin", "dest"]
SCHEDULE = ["crs_dep_hour", "dow", "month", "distance"]
HISTORY = ["origin_prior7d_rate", "airline_prior7d_rate"]
PREV = ["prev_leg_arr_delay"]
SAMEDAY = ["origin_last3h_rate", "origin_last3h_avg_delay"]

EXPERIMENTS = {
    "Departure hour only": (["crs_dep_hour"], []),
    "Schedule + airline/airports": (SCHEDULE, CATS),
    "  + prior 7-day delay rates": (SCHEDULE + HISTORY, CATS),
    "  + previous leg of same aircraft": (SCHEDULE + PREV, CATS),
    "  + same-day airport conditions (last 3h)": (SCHEDULE + SAMEDAY, CATS),
    "  + previous leg and same-day conditions": (SCHEDULE + PREV + SAMEDAY, CATS),
    "All features": (SCHEDULE + HISTORY + PREV + SAMEDAY, CATS),
}


def make_model(nums, cats):
    parts = [("num", "passthrough", nums)]
    if cats:
        parts.append(("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=np.nan,
                                            encoded_missing_value=np.nan, max_categories=100), cats))
    cat_idx = list(range(len(nums), len(nums) + len(cats))) if cats else None
    return Pipeline([("prep", ColumnTransformer(parts)),
                     ("clf", HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08, max_leaf_nodes=31,
                                                            categorical_features=cat_idx, random_state=42))])


def run(train, val, test, nums, cats):
    cols = nums + cats
    y_tr, y_va, y_te = (d["dep_del15"].astype(int) for d in (train, val, test))
    model = make_model(nums, cats).fit(train[cols], y_tr)
    thr = dm.best_threshold(y_va, model.predict_proba(val[cols])[:, 1])
    return dm.evaluate(y_te, model.predict_proba(test[cols])[:, 1], thr)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", default=str(ROOT / "data" / "processed" / "flights_clean.parquet"))
    a = ap.parse_args()
    raw = pd.read_parquet(a.parquet)

    # Part 1: feature ablation at a 60 minute lead time
    df = dm.build_features(raw, 60)
    train, val, test = dm.chronological_split(df)
    base = test["dep_del15"].mean()
    rows1 = []
    for name, (nums, cats) in EXPERIMENTS.items():
        r = run(train, val, test, nums, cats)
        rows1.append((name, r))
        print(f"{name:36s} ROC-AUC {r['ROC-AUC']:.3f}  PR-AUC {r['PR-AUC']:.3f}")

    # Part 2: lead time, all features
    rows2 = []
    for lead in (60, 120, 180):
        d = dm.build_features(raw, lead)
        tr, va, te = dm.chronological_split(d)
        r = run(tr, va, te, SCHEDULE + HISTORY + PREV + SAMEDAY, CATS)
        rows2.append((lead, d["prev_leg_arr_delay"].notna().mean(), r))
        print(f"lead {lead:3d} min  prev-leg available {rows2[-1][1]:.1%}  ROC-AUC {r['ROC-AUC']:.3f}  PR-AUC {r['PR-AUC']:.3f}")

    n_days = df["date"].nunique()
    n_months = df["date"].dt.to_period("M").nunique()
    L = ["# Model Ablation and Lead-Time Results", "",
         f"Gradient boosting, {len(df):,} non-cancelled flights over {n_days} days in {n_months} months, chronological split "
         f"({dm.describe_split(train, val, test)}), "
         f"test-set delay rate {base:.1%}. PR-AUC of a model with no skill equals the delay rate.", "",
         "## Feature ablation (prediction 60 minutes before departure)", "",
         "| Feature set | ROC-AUC | PR-AUC | Precision | Recall | F1 |", "|---|---:|---:|---:|---:|---:|"]
    L += [f"| {n.strip()} | {r['ROC-AUC']:.3f} | {r['PR-AUC']:.3f} | {r['Precision']:.3f} | {r['Recall']:.3f} | {r['F1']:.3f} |"
          for n, r in rows1]
    L += ["", "## Lead time (all features)", "",
          "| Prediction made | Previous-leg feature available | ROC-AUC | PR-AUC | Precision | Recall | F1 |",
          "|---|---:|---:|---:|---:|---:|---:|"]
    L += [f"| {lead} min before departure | {av:.1%} | {r['ROC-AUC']:.3f} | {r['PR-AUC']:.3f} | "
          f"{r['Precision']:.3f} | {r['Recall']:.3f} | {r['F1']:.3f} |" for lead, av, r in rows2]
    if n_days < 90:
        L += ["", f"Note: only {n_days} days of data. Differences of a few thousandths between rows are within noise."]
    (ROOT / "documentation" / "ablation_results.md").write_text("\n".join(L) + "\n")
    print("\nWrote documentation/ablation_results.md")


if __name__ == "__main__":
    main()
