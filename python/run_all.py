"""Run the whole pipeline in order: clean, build warehouse, SQL analysis, Power BI export,
delay model, results digest. Run from anywhere; paths are resolved from this file.

Usage:
    python python/run_all.py                 # everything on data/raw/*.csv
    python python/run_all.py --skip-model    # skip the (slow on big data) model step
    python python/run_all.py --with-ablation # also run the feature ablation and lead-time comparison
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = ["01_clean_flights.py", "02_build_warehouse.py", "03_run_sql_analysis.py",
         "04_export_powerbi.py", "05_delay_model.py", "06_summarize_results.py", "08_make_charts.py"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-model", action="store_true")
    ap.add_argument("--with-ablation", action="store_true")
    a = ap.parse_args()
    steps = STEPS + (["07_model_ablation.py"] if a.with_ablation else [])
    for step in steps:
        if a.skip_model and step == "05_delay_model.py":
            continue
        print(f"\n=== {step} ===", flush=True)
        r = subprocess.run([sys.executable, str(HERE / step)])
        if r.returncode != 0:
            raise SystemExit(f"{step} failed (exit code {r.returncode}). Fix that step, then rerun.")
    print("\nAll steps finished. Key outputs are in documentation/ and powerbi/data/.")


if __name__ == "__main__":
    main()
