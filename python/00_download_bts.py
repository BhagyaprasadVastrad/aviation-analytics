"""Download BTS Airline On-Time Performance monthly files into data/raw/.

Usage:
    python python/00_download_bts.py --year 2024 --month 6
    python python/00_download_bts.py --year 2024 --months 1-12
    python python/00_download_bts.py --year 2024 --months 2,9,12     # specific months
    python python/00_download_bts.py --year 2024 --quarterly         # Feb, Jun, Sep, Dec (one per quarter)

Months already present in data/raw/ are skipped.

If the download fails (BTS occasionally changes URLs or blocks scripts), get the file
manually: transtats.bts.gov > Aviation > Airline On-Time Performance Data >
"Reporting Carrier On-Time Performance (1987-present)" > Download > select all fields,
filter year/month, and save the unzipped CSV into data/raw/.
"""
import argparse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
URL = ("https://transtats.bts.gov/PREZIP/"
       "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{year}_{month}.zip")


QUARTERLY = [2, 6, 9, 12]


def parse_months(spec: str):
    """'1-12' -> 1..12, '2,9,12' -> [2, 9, 12], '3' -> [3]."""
    months = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = map(int, part.split("-"))
            months.extend(range(lo, hi + 1))
        else:
            months.append(int(part))
    if not months or any(m < 1 or m > 12 for m in months):
        raise ValueError(f"Invalid months: {spec}")
    return sorted(set(months))


def download(year: int, month: int) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    if (RAW / f"bts_{year}_{month:02d}.csv").exists():
        print(f"Skipping {year}-{month:02d}: already in data/raw/")
        return
    url = URL.format(year=year, month=month)
    zpath = RAW / f"bts_{year}_{month:02d}.zip"
    print(f"Downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as r, open(zpath, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    with zipfile.ZipFile(zpath) as z:
        for n in [n for n in z.namelist() if n.lower().endswith(".csv")]:
            target = RAW / f"bts_{year}_{month:02d}.csv"
            with z.open(n) as src, open(target, "wb") as dst:
                dst.write(src.read())
            print(f"  -> {target.name}")
    zpath.unlink()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--month", type=int)
    g.add_argument("--months", type=str, help="range or list, such as 1-12 or 2,9,12")
    g.add_argument("--quarterly", action="store_true", help="one month per quarter: Feb, Jun, Sep, Dec")
    a = ap.parse_args()
    if a.month:
        months = [a.month]
    elif a.quarterly:
        months = QUARTERLY
    else:
        months = parse_months(a.months)
    for m in months:
        download(a.year, m)


if __name__ == "__main__":
    main()
