"""Summarise the SQL result CSVs into one readable file: documentation/results_digest.md

Usage:
    python python/06_summarize_results.py
"""
import calendar
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "data" / "processed" / "results"


def md(df: pd.DataFrame) -> str:
    df = df.copy()
    for c in df.columns:
        if pd.api.types.is_float_dtype(df[c]):
            df[c] = df[c].round(2)
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    fmt = lambda v: "" if pd.isna(v) else (f"{v:,}" if isinstance(v, int) else str(v))
    rows = ["| " + " | ".join(fmt(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join([head, sep] + rows)


def pivot_by_month(df: pd.DataFrame, index: str, value: str) -> pd.DataFrame:
    """Rows = `index`, one column per month in calendar order."""
    df = df.copy()
    if "month_name" not in df.columns:
        df["month_name"] = df["month"].map(lambda m: calendar.month_abbr[int(m)])
    order = df.drop_duplicates("month").sort_values("month")["month_name"].tolist()
    return df.pivot_table(index=index, columns="month_name", values=value, aggfunc="first")[order].reset_index()


def cancellations_pivot(df: pd.DataFrame) -> pd.DataFrame:
    pv = pivot_by_month(df, "reason", "cancellations")
    cols = [c for c in pv.columns if c != "reason"]
    pv[cols] = pv[cols].fillna(0).astype(int)
    return pv


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(RES / f"{name}.csv")


def main() -> None:
    out = ["# Results Digest", "",
           "Generated from data/processed/results/*.csv. Rates are percentages. "
           "On-time = completed flight arriving less than 15 minutes late.", ""]

    a = load("03_airline_analysis__1")
    out += ["## Airline scorecard (sorted by on-time %)", "", md(a), ""]

    ap = load("04_airport_analysis__1")
    cols = ["origin_airport", "city", "departures", "dep_delay_rate_pct", "avg_dep_delay_min",
            "avg_taxi_out_min", "cancellation_rate_pct"]
    out += ["## Origin airports: 10 worst by departure delay rate (min 500 departures)", "",
            md(ap[cols].head(10)), "",
            "## Origin airports: 10 best", "", md(ap[cols].tail(10).iloc[::-1]), ""]
    big = ap.sort_values("departures", ascending=False).head(15)
    out += ["## 15 busiest origin airports", "", md(big[cols]), ""]

    out += ["## Routes: 15 worst by arrival delay rate (min 100 flights)", "",
            md(load("05_route_analysis__1").head(15)), ""]
    out += ["## Day of week", "", md(load("05_route_analysis__2")), ""]
    out += ["## Scheduled departure hour", "", md(load("05_route_analysis__3")), ""]
    out += ["## Distance band", "", md(load("05_route_analysis__5")), ""]
    out += ["## Delay cause share of delay minutes (flights 15+ min late on arrival)", "",
            md(load("06_delay_causes_analysis__1")), ""]
    out += ["## Cause mix by airline", "", md(load("06_delay_causes_analysis__2")), ""]
    out += ["## Cancellation reasons", "", md(load("06_delay_causes_analysis__4")), ""]
    out += ["## Late-aircraft propagation (next departure by inbound status of same aircraft)", "",
            md(load("06_delay_causes_analysis__5")), ""]

    # Seasonal comparison (one column per loaded month)
    out += ["# Seasonal Comparison", ""]
    out += ["## Monthly scorecard", "", md(load("05_route_analysis__7")), ""]
    out += ["## Departure delay rate by scheduled hour and month (%)", "",
            md(pivot_by_month(load("05_route_analysis__6"), "crs_dep_hour", "dep_delay_rate_pct")), ""]
    out += ["## Airline on-time arrival % by month", "",
            md(pivot_by_month(load("03_airline_analysis__2"), "airline_name", "on_time_pct")), ""]
    out += ["## Airline rank by month (1 = best on-time %)", "",
            md(pivot_by_month(load("03_airline_analysis__2"), "airline_name", "monthly_rank")), ""]
    out += ["## Busiest 15 airports: departure delay rate by month (%)", "",
            md(pivot_by_month(load("04_airport_analysis__5"), "origin_airport", "dep_delay_rate_pct")), ""]
    out += ["## Delay cause mix by month (share of delay minutes, %)", "",
            md(load("06_delay_causes_analysis__3")), ""]
    out += ["## Cancellations by reason and month", "",
            md(cancellations_pivot(load("06_delay_causes_analysis__6"))), ""]

    path = ROOT / "documentation" / "results_digest.md"
    path.write_text("\n".join(out))
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
