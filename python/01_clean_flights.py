"""Clean raw BTS monthly CSVs and write one analysis-ready Parquet file.

Usage:
    python python/01_clean_flights.py                       # all CSVs in data/raw/
    python python/01_clean_flights.py --input data/sample/sample_flights.csv

Outputs:
    data/processed/flights_clean.parquet
    documentation/data_quality_report.md
"""
import argparse
import glob
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

RENAME = {
    "FlightDate": "flight_date",
    "Reporting_Airline": "airline_code",
    "Tail_Number": "tail_number",
    "Flight_Number_Reporting_Airline": "flight_number",
    "Origin": "origin", "OriginCityName": "origin_city", "OriginState": "origin_state",
    "Dest": "dest", "DestCityName": "dest_city", "DestState": "dest_state",
    "CRSDepTime": "crs_dep_time", "DepTime": "dep_time", "DepDelay": "dep_delay",
    "DepDel15": "dep_del15", "DepTimeBlk": "dep_time_blk",
    "TaxiOut": "taxi_out", "TaxiIn": "taxi_in",
    "CRSArrTime": "crs_arr_time", "ArrTime": "arr_time", "ArrDelay": "arr_delay",
    "ArrDel15": "arr_del15",
    "Cancelled": "cancelled", "CancellationCode": "cancellation_code", "Diverted": "diverted",
    "CRSElapsedTime": "crs_elapsed_time", "AirTime": "air_time", "Distance": "distance",
    "CarrierDelay": "carrier_delay", "WeatherDelay": "weather_delay", "NASDelay": "nas_delay",
    "SecurityDelay": "security_delay", "LateAircraftDelay": "late_aircraft_delay",
}
USECOLS = set(RENAME)
DEDUP_KEY = ["flight_date", "airline_code", "flight_number", "origin", "dest",
             "crs_dep_time", "tail_number"]


def hhmm_to_minutes(s: pd.Series) -> pd.Series:
    """Convert BTS hhmm (e.g. 1435) to minutes after midnight. 2400 -> 0. Invalid -> NaN."""
    s = pd.to_numeric(s, errors="coerce")
    mins = (s // 100) * 60 + (s % 100)
    mins = mins.where((s % 100) < 60)
    return mins.mod(1440)


def clean(df: pd.DataFrame):
    q = {"rows_raw": len(df)}
    df = df.rename(columns=RENAME)

    df["flight_date"] = pd.to_datetime(df["flight_date"], errors="coerce")
    q["invalid_flight_date"] = int(df["flight_date"].isna().sum())
    df = df.dropna(subset=["flight_date", "airline_code", "origin", "dest"])

    for c in ["airline_code", "origin", "dest", "tail_number", "cancellation_code"]:
        df[c] = df[c].astype("string").str.strip().str.upper()
    df["cancelled"] = df["cancelled"].fillna(0).astype(int)
    df["diverted"] = df["diverted"].fillna(0).astype(int)

    before = len(df)
    df = df.drop_duplicates(subset=DEDUP_KEY, keep="first")
    q["duplicates_removed"] = before - len(df)

    for c in ["crs_dep_time", "dep_time", "crs_arr_time", "arr_time"]:
        df[c.replace("_time", "_min")] = hhmm_to_minutes(df[c])
    q["invalid_crs_dep_time"] = int(df["crs_dep_min"].isna().sum())
    df = df.dropna(subset=["crs_dep_min"])
    df["crs_dep_ts"] = df["flight_date"] + pd.to_timedelta(df["crs_dep_min"], unit="m")
    df["crs_dep_hour"] = (df["crs_dep_min"] // 60).astype(int)

    df["flight_status"] = np.select(
        [df["cancelled"] == 1, df["diverted"] == 1], ["Cancelled", "Diverted"], "Completed")

    q["origin_equals_dest"] = int((df["origin"] == df["dest"]).sum())
    q["nonpositive_distance"] = int((df["distance"] <= 0).sum())
    q["cancelled_with_dep_time"] = int(((df["cancelled"] == 1) & df["dep_time"].notna()).sum())
    q["completed_missing_arr_delay"] = int(
        ((df["flight_status"] == "Completed") & df["arr_delay"].isna()).sum())
    q["completed_missing_dep_delay"] = int(
        ((df["flight_status"] == "Completed") & df["dep_delay"].isna()).sum())
    q["extreme_dep_delay_over_24h"] = int((df["dep_delay"].abs() > 1440).sum())

    # BTS can record a departure time for flights cancelled after pushback. Their delay values are
    # not valid performance data, so blank every actual-performance field on cancelled flights.
    blank_cols = ["dep_time", "arr_time", "dep_delay", "arr_delay", "taxi_out", "taxi_in", "air_time",
                  "carrier_delay", "weather_delay", "nas_delay", "security_delay", "late_aircraft_delay"]
    q["cancelled_actuals_blanked"] = int(((df["cancelled"] == 1) & df["dep_delay"].notna()).sum())
    df.loc[df["cancelled"] == 1, blank_cols] = np.nan
    df.loc[df["cancelled"] == 1, ["dep_min", "arr_min"]] = np.nan

    # Recompute 15-minute flags so they always agree with the delay minutes
    df["dep_del15"] = np.where(df["dep_delay"].notna(), (df["dep_delay"] >= 15).astype(float), np.nan)
    df["arr_del15"] = np.where(df["arr_delay"].notna(), (df["arr_delay"] >= 15).astype(float), np.nan)

    keep = ["flight_date", "crs_dep_ts", "airline_code", "flight_number", "tail_number",
            "origin", "origin_city", "origin_state", "dest", "dest_city", "dest_state",
            "crs_dep_min", "crs_dep_hour", "dep_min", "dep_time_blk", "crs_arr_min", "arr_min",
            "dep_delay", "dep_del15", "arr_delay", "arr_del15",
            "taxi_out", "taxi_in", "air_time", "crs_elapsed_time", "distance",
            "cancelled", "cancellation_code", "diverted", "flight_status",
            "carrier_delay", "weather_delay", "nas_delay", "security_delay",
            "late_aircraft_delay"]
    df = df[keep].reset_index(drop=True)
    q["rows_clean"] = len(df)
    return df, q


def write_report(q: dict, df: pd.DataFrame, path: Path) -> None:
    status = df["flight_status"].value_counts()
    lines = ["# Data Quality Report", "",
             f"Date range: {df['flight_date'].min().date()} to {df['flight_date'].max().date()}", "",
             "## Cleaning log", "", "| Check | Rows |", "|---|---:|"]
    lines += [f"| {k} | {v:,} |" for k, v in q.items()]
    lines += ["", "## Flight status", "", "| Status | Rows | Share |", "|---|---:|---:|"]
    lines += [f"| {k} | {v:,} | {v / len(df):.2%} |" for k, v in status.items()]
    lines += ["", "## Notes", "",
              "- Delay-cause columns are only populated by BTS for flights with arrival delay of 15+ minutes; they are null otherwise.",
              "- Cancelled flights keep their rows but all actual-performance fields (times, delays, taxi, air time) are blanked, including the BTS cases where a departure time was recorded before cancellation. Diverted flights keep departure delay but have no arrival delay.",
              "- dep_del15 and arr_del15 are recomputed from the delay minutes so they cannot disagree."]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="*", help="CSV file(s); default is data/raw/*.csv")
    ap.add_argument("--output", default=str(ROOT / "data" / "processed" / "flights_clean.parquet"))
    a = ap.parse_args()
    files = a.input or sorted(glob.glob(str(ROOT / "data" / "raw" / "*.csv")))
    if not files:
        raise SystemExit("No input CSVs found. Run 00_download_bts.py first.")
    frames = []
    for f in files:
        print(f"Reading {f}")
        frames.append(pd.read_csv(f, usecols=lambda c: c in USECOLS, low_memory=False))
    df, q = clean(pd.concat(frames, ignore_index=True))
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(a.output, index=False)
    write_report(q, df, ROOT / "documentation" / "data_quality_report.md")
    for k, v in q.items():
        print(f"{k:32s} {v:>12,}")
    print(f"Wrote {a.output}")


if __name__ == "__main__":
    main()
