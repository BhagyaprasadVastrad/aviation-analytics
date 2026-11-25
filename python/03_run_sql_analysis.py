"""Run every analysis query in sql/ against the warehouse and save each result as CSV.

Usage:
    python python/03_run_sql_analysis.py

Outputs:
    data/processed/results/<sql_file>__<n>.csv
    documentation/validation_results.md   (the data validation checks, readable)
"""
import argparse
import re
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
SQL_FILES = ["02_data_validation", "03_airline_analysis", "04_airport_analysis",
             "05_route_analysis", "06_delay_causes_analysis"]


def statements(text: str):
    # Split on semicolons, keep only statements that contain a SELECT
    return [s.strip() for s in text.split(";") if re.search(r"\bSELECT\b", s, re.I)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(ROOT / "data" / "processed" / "aviation.duckdb"))
    a = ap.parse_args()
    out_dir = ROOT / "data" / "processed" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(a.db, read_only=True)
    report = ["# Validation Results", ""]
    for name in SQL_FILES:
        stmts = statements((ROOT / "sql" / f"{name}.sql").read_text())
        for i, s in enumerate(stmts, 1):
            df = con.execute(s).df()
            df.to_csv(out_dir / f"{name}__{i}.csv", index=False)
            print(f"{name} [{i}] -> {len(df):,} rows")
            if name == "02_data_validation":
                report += [f"## Check {i}", "", "```", df.to_string(index=False), "```", ""]
    (ROOT / "documentation" / "validation_results.md").write_text("\n".join(report))
    print(f"\nResults in {out_dir}")
    print("Validation output saved to documentation/validation_results.md")


if __name__ == "__main__":
    main()
