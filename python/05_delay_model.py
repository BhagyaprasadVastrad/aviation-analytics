"""Predict whether a flight will have a departure delay of 15+ minutes, using only information
available before departure.

Usage:
    python python/05_delay_model.py
    python python/05_delay_model.py --parquet data/processed/flights_clean.parquet --lead-minutes 60

Leakage controls
- Target: dep_del15. Cancelled flights are excluded.
- Features: schedule (hour, weekday, month), airline, origin, destination, distance, and history:
    * origin airport and airline delay rate over the PRIOR 7 calendar days (current day excluded)
    * previous leg of the same aircraft (tail number), used only if that flight had already landed
      at this airport at least --lead-minutes before scheduled departure
    * same-day airport conditions: delay rate and average delay of flights from the same origin that
      had already departed in the 3 hours before the prediction time
- Never used: actual times, arrival delay (of this flight), taxi, air time, delay-cause columns.
- Split: chronological. With 4+ months of data, whole months (last = test, previous = validation,
  rest = train); otherwise by days (first 60% train, next 20% validation, last 20% test).
  The decision threshold is chosen on validation and applied once to test.

Outputs: documentation/model_results.md, models/*.joblib
"""
import argparse
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CATS = ["airline_code", "origin", "dest"]
NUMS = ["crs_dep_hour", "dow", "month", "distance", "origin_prior7d_rate",
        "airline_prior7d_rate", "prev_leg_arr_delay", "origin_last3h_rate", "origin_last3h_avg_delay"]


def prior_rate(df: pd.DataFrame, key: str, name: str, days: int = 7) -> pd.DataFrame:
    """Delay rate of `key` over the previous `days` calendar days, excluding the current day."""
    daily = (df.groupby([key, "date"])["dep_del15"].agg(s="sum", n="count")
               .reset_index().sort_values("date").set_index("date"))
    roll = daily.groupby(key)[["s", "n"]].rolling(f"{days}D", closed="left").sum().reset_index()
    roll[name] = roll["s"] / roll["n"]
    return roll[[key, "date", name]]


def same_day_conditions(df: pd.DataFrame, lead_minutes: int, window_hours: int = 3, min_flights: int = 5):
    """Delay rate and average delay of flights from the same origin that had ALREADY departed
    (actual departure time at or before the prediction time) in the previous `window_hours` hours.
    The flight's own row is excluded from its window."""
    ns = lambda x: x.values.astype("datetime64[ns]").astype("int64")
    act = ns(df["crs_dep_ts"] + pd.to_timedelta(df["dep_delay"], unit="m"))
    cutoff = ns(df["crs_dep_ts"] - pd.Timedelta(minutes=lead_minutes))
    win = int(window_hours * 3600 * 1e9)
    d15 = df["dep_del15"].to_numpy(float)
    dd = df["dep_delay"].clip(-60, 300).to_numpy(float)
    rate = np.full(len(df), np.nan)
    avg = np.full(len(df), np.nan)
    for _, idx in df.groupby("origin").indices.items():
        a = act[idx]
        order = np.argsort(a, kind="stable")
        a_s = a[order]
        c15 = np.concatenate([[0.0], np.cumsum(d15[idx][order])])
        cd = np.concatenate([[0.0], np.cumsum(dd[idx][order])])
        co = cutoff[idx]
        hi = np.searchsorted(a_s, co, side="right")
        lo = np.searchsorted(a_s, co - win, side="right")
        n = (hi - lo).astype(float)
        s15 = c15[hi] - c15[lo]
        sd = cd[hi] - cd[lo]
        self_in = (a <= co) & (a > co - win)
        n -= self_in
        s15 -= self_in * d15[idx]
        sd -= self_in * dd[idx]
        ok = n >= min_flights
        rate[idx] = np.where(ok, s15 / np.maximum(n, 1), np.nan)
        avg[idx] = np.where(ok, sd / np.maximum(n, 1), np.nan)
    return rate, avg


def build_features(df: pd.DataFrame, lead_minutes: int) -> pd.DataFrame:
    df = df[(df["flight_status"] != "Cancelled") & df["dep_delay"].notna()].copy()
    df["date"] = df["flight_date"].dt.normalize()
    df["dow"] = df["flight_date"].dt.dayofweek
    df["month"] = df["flight_date"].dt.month

    df = df.merge(prior_rate(df, "origin", "origin_prior7d_rate"), on=["origin", "date"], how="left")
    df = df.merge(prior_rate(df, "airline_code", "airline_prior7d_rate"), on=["airline_code", "date"], how="left")

    # Previous leg of the same aircraft, known only if it had landed here before the prediction time
    df = df.sort_values(["tail_number", "crs_dep_ts"]).reset_index(drop=True)
    g = df.groupby("tail_number", sort=False)
    df["prev_dest"] = g["dest"].shift()
    df["prev_arr_delay"] = g["arr_delay"].shift()
    df["prev_act_arr_ts"] = (g["crs_dep_ts"].shift()
                             + pd.to_timedelta(g["crs_elapsed_time"].shift().fillna(0)
                                               + df["prev_arr_delay"].fillna(0), unit="m"))
    cutoff = df["crs_dep_ts"] - pd.Timedelta(minutes=lead_minutes)
    known = ((df["prev_dest"] == df["origin"]) & df["prev_arr_delay"].notna()
             & (df["prev_act_arr_ts"] <= cutoff)
             & (df["crs_dep_ts"] - df["prev_act_arr_ts"] <= pd.Timedelta(days=1)))
    df["prev_leg_arr_delay"] = np.where(known, df["prev_arr_delay"], np.nan)
    df["origin_last3h_rate"], df["origin_last3h_avg_delay"] = same_day_conditions(df, lead_minutes)

    return df.sort_values("crs_dep_ts").reset_index(drop=True)


def chronological_split(df: pd.DataFrame):
    """Chronological split. With 4 or more calendar months of data, split on whole months
    (last month = test, the one before = validation, the rest = train). With less, split by days
    (first 60% train, next 20% validation, last 20% test)."""
    months = df["date"].dt.to_period("M")
    uniq = sorted(months.unique())
    if len(uniq) >= 4:
        return df[months < uniq[-2]], df[months == uniq[-2]], df[months == uniq[-1]]
    days = np.sort(df["date"].unique())
    a, b = days[int(len(days) * 0.6)], days[int(len(days) * 0.8)]
    return df[df["date"] < a], df[(df["date"] >= a) & (df["date"] < b)], df[df["date"] >= b]


def describe_split(train, val, test) -> str:
    rng = lambda d: f"{d['date'].min().date()} to {d['date'].max().date()}"
    return f"train {rng(train)}, validation {rng(val)}, test {rng(test)}"


def models():
    num_lin = Pipeline([("imp", SimpleImputer(strategy="median", add_indicator=True)), ("sc", StandardScaler())])
    num_tree = SimpleImputer(strategy="median", add_indicator=True)
    lr = Pipeline([
        ("prep", ColumnTransformer([("num", num_lin, NUMS),
                                    ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=50), CATS)])),
        ("clf", LogisticRegression(max_iter=1000))])
    rf = Pipeline([
        ("prep", ColumnTransformer([("num", num_tree, NUMS),
                                    ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), CATS)])),
        ("clf", RandomForestClassifier(n_estimators=150, min_samples_leaf=50, max_samples=0.5,
                                       n_jobs=-1, random_state=42))])
    # Gradient boosting: categorical columns are capped at 100 levels (rare ones grouped together)
    hgb = Pipeline([
        ("prep", ColumnTransformer([("num", "passthrough", NUMS),
                                    ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=np.nan,
                                                           encoded_missing_value=np.nan, max_categories=100), CATS)])),
        ("clf", HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08, max_leaf_nodes=31,
                                               categorical_features=list(range(len(NUMS), len(NUMS) + len(CATS))),
                                               random_state=42))])
    return {"Logistic regression": lr, "Random forest": rf, "Gradient boosting": hgb}


def best_threshold(y, p) -> float:
    grid = np.linspace(0.05, 0.8, 76)
    return float(grid[int(np.argmax([f1_score(y, p >= t, zero_division=0) for t in grid]))])


def evaluate(y, p, thr) -> dict:
    pred = p >= thr
    tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
    return {"ROC-AUC": roc_auc_score(y, p), "PR-AUC": average_precision_score(y, p),
            "Threshold": thr, "Precision": precision_score(y, pred, zero_division=0),
            "Recall": recall_score(y, pred), "F1": f1_score(y, pred), "TN": tn, "FP": fp, "FN": fn, "TP": tp}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", default=str(ROOT / "data" / "processed" / "flights_clean.parquet"))
    ap.add_argument("--lead-minutes", type=int, default=60, help="prediction made this long before departure")
    a = ap.parse_args()

    raw = pd.read_parquet(a.parquet)
    df = build_features(raw, a.lead_minutes)
    train, val, test = chronological_split(df)
    n_days = df["date"].nunique()
    n_months = df["date"].dt.to_period("M").nunique()
    print(f"{len(df):,} flights over {n_days} days in {n_months} months | train {len(train):,} val {len(val):,} test {len(test):,}")
    print(f"Departure delay rate: train {train.dep_del15.mean():.1%}, val {val.dep_del15.mean():.1%}, "
          f"test {test.dep_del15.mean():.1%}")
    print(f"Previous-leg feature available for {df['prev_leg_arr_delay'].notna().mean():.1%} of flights")

    X = lambda d: d[NUMS + CATS]
    y_tr, y_va, y_te = train["dep_del15"].astype(int), val["dep_del15"].astype(int), test["dep_del15"].astype(int)

    rows = {}
    base = test["dep_del15"].mean()
    rows["Majority class (no model)"] = {"ROC-AUC": 0.5, "PR-AUC": base, "Threshold": np.nan, "Precision": 0.0,
                                         "Recall": 0.0, "F1": 0.0, "TN": int((y_te == 0).sum()), "FP": 0, "FN": int(y_te.sum()), "TP": 0}
    fill = train["origin_prior7d_rate"].mean()
    s_va, s_te = val["origin_prior7d_rate"].fillna(fill), test["origin_prior7d_rate"].fillna(fill)
    rows["Baseline: origin 7-day delay rate"] = evaluate(y_te, s_te.values, best_threshold(y_va, s_va.values))

    (ROOT / "models").mkdir(exist_ok=True)
    for name, model in models().items():
        t0 = time.time()
        model.fit(X(train), y_tr)
        thr = best_threshold(y_va, model.predict_proba(X(val))[:, 1])
        rows[name] = evaluate(y_te, model.predict_proba(X(test))[:, 1], thr)
        joblib.dump(model, ROOT / "models" / f"{name.lower().replace(' ', '_')}.joblib")
        print(f"{name:22s} ROC-AUC {rows[name]['ROC-AUC']:.3f}  PR-AUC {rows[name]['PR-AUC']:.3f}  ({time.time() - t0:.0f}s)")

    res = pd.DataFrame(rows).T
    lines = ["# Delay Prediction Results", "",
             f"Target: departure delay of 15+ minutes. Prediction made {a.lead_minutes} minutes before scheduled departure.",
             f"Data: {len(df):,} non-cancelled flights across {n_days} days in {n_months} calendar months "
             f"({df['date'].min().date()} to {df['date'].max().date()}).",
             f"Split: chronological ({describe_split(train, val, test)}). "
             f"Train {len(train):,} / validation {len(val):,} / test {len(test):,}.",
             f"Test-set delay rate: {base:.1%}. Threshold chosen on validation to maximise F1, applied once to test.", "",
             "| Model | ROC-AUC | PR-AUC | Precision | Recall | F1 | Threshold |", "|---|---:|---:|---:|---:|---:|---:|"]
    for n, r in res.iterrows():
        thr = "" if np.isnan(r["Threshold"]) else f"{r['Threshold']:.2f}"
        lines.append(f"| {n} | {r['ROC-AUC']:.3f} | {r['PR-AUC']:.3f} | {r['Precision']:.3f} | {r['Recall']:.3f} | {r['F1']:.3f} | {thr} |")
    lines += ["", "Confusion matrices (test set):", "", "| Model | TN | FP | FN | TP |", "|---|---:|---:|---:|---:|"]
    lines += [f"| {n} | {int(r.TN):,} | {int(r.FP):,} | {int(r.FN):,} | {int(r.TP):,} |" for n, r in res.iterrows()]
    if n_days < 90:
        lines += ["", f"Note: only {n_days} days of data. Seasonal effects cannot be learned and the test window is short. "
                      "Treat these numbers as a pipeline check until more months are loaded."]
    elif n_months < 12:
        lines += ["", f"Note: {n_months} calendar months of data. The test month is a season the model has not "
                      "seen in training, so results show how well it carries over to a new season."]
    (ROOT / "documentation" / "model_results.md").write_text("\n".join(lines) + "\n")
    print("\nWrote documentation/model_results.md")


if __name__ == "__main__":
    main()
