"""Export the star schema tables to Parquet for Power BI Desktop (Get Data > Parquet).

Usage:
    python python/04_export_powerbi.py

Output: powerbi/data/<table>.parquet
"""
import argparse
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
TABLES = ["fact_flights", "dim_airline", "dim_airport", "dim_date", "dim_route"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(ROOT / "data" / "processed" / "aviation.duckdb"))
    a = ap.parse_args()
    out = ROOT / "powerbi" / "data"
    out.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(a.db, read_only=True)
    for t in TABLES:
        path = (out / f"{t}.parquet").as_posix()
        con.execute(f"COPY {t} TO '{path}' (FORMAT PARQUET)")
        n = con.execute(f"select count(*) from {t}").fetchone()[0]
        print(f"{t:14s} {n:>10,} rows -> {path}")


if __name__ == "__main__":
    main()
