"""Build the DuckDB star schema from the cleaned parquet.

Usage:
    python python/02_build_warehouse.py
Output:
    data/processed/aviation.duckdb
"""
import argparse
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", default=str(ROOT / "data" / "processed" / "flights_clean.parquet"))
    ap.add_argument("--db", default=str(ROOT / "data" / "processed" / "aviation.duckdb"))
    a = ap.parse_args()
    sql = (ROOT / "sql" / "01_build_star_schema.sql").read_text()
    sql = sql.replace("{{PARQUET}}", Path(a.parquet).as_posix())
    con = duckdb.connect(a.db)
    con.execute(sql)
    for t in ["fact_flights", "dim_airline", "dim_airport", "dim_date", "dim_route"]:
        print(f"{t:14s} {con.execute(f'select count(*) from {t}').fetchone()[0]:>10,} rows")
    con.close()
    print(f"Built {a.db}")


if __name__ == "__main__":
    main()
