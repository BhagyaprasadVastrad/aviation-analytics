"""Generate SYNTHETIC flight data in the BTS column format.

For testing the pipeline only. Never use this for findings: the delay patterns are made up.

Usage:
    python python/make_sample_data.py --rows 30000
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AIRPORTS = {"ATL": ("Atlanta, GA", "GA"), "ORD": ("Chicago, IL", "IL"), "DFW": ("Dallas/Fort Worth, TX", "TX"),
            "DEN": ("Denver, CO", "CO"), "LAX": ("Los Angeles, CA", "CA"), "JFK": ("New York, NY", "NY"),
            "SFO": ("San Francisco, CA", "CA"), "SEA": ("Seattle, WA", "WA"), "MIA": ("Miami, FL", "FL"),
            "BOS": ("Boston, MA", "MA")}
CARRIERS = ["AA", "DL", "UA", "WN", "B6", "AS", "NK"]


def to_hhmm(minutes):
    m = np.asarray(minutes) % 1440
    return (m // 60) * 100 + (m % 60)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=30000)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    n = a.rows
    codes = list(AIRPORTS)
    origin = rng.choice(codes, n)
    dest = np.array([rng.choice([c for c in codes if c != o]) for o in origin])
    date = pd.to_datetime("2024-06-01") + pd.to_timedelta(rng.integers(0, 30, n), unit="D")
    crs_dep = rng.integers(5 * 60, 23 * 60 + 59, n)
    carrier = rng.choice(CARRIERS, n)
    dist = rng.integers(200, 2700, n)
    elapsed = (dist / 7.5 + 30).astype(int)

    # Made-up delay structure: evening, weekend, hub and carrier effects
    base = -3 + 0.012 * (crs_dep - 5 * 60) / 60 * 60 / 10
    base += np.where(np.isin(origin, ["ORD", "JFK", "ATL"]), 6, 0)
    base += np.where(carrier == "NK", 5, 0)
    dep_delay = np.round(base + rng.exponential(9, n) - 6).astype(float)
    cancelled = rng.random(n) < 0.018
    diverted = (~cancelled) & (rng.random(n) < 0.002)
    arr_delay = np.round(dep_delay + rng.normal(0, 8, n)).astype(float)

    df = pd.DataFrame({
        "FlightDate": date.strftime("%Y-%m-%d"), "Reporting_Airline": carrier,
        "Tail_Number": ["N" + str(x) for x in rng.integers(100, 400, n)],
        "Flight_Number_Reporting_Airline": rng.integers(1, 4000, n),
        "Origin": origin, "OriginCityName": [AIRPORTS[o][0] for o in origin],
        "OriginState": [AIRPORTS[o][1] for o in origin],
        "Dest": dest, "DestCityName": [AIRPORTS[d][0] for d in dest],
        "DestState": [AIRPORTS[d][1] for d in dest],
        "CRSDepTime": to_hhmm(crs_dep), "DepTime": to_hhmm(crs_dep + dep_delay),
        "DepDelay": dep_delay, "DepDel15": (dep_delay >= 15).astype(float),
        "DepTimeBlk": [f"{h:02d}00-{h:02d}59" for h in (crs_dep // 60)],
        "TaxiOut": rng.integers(8, 40, n).astype(float), "TaxiIn": rng.integers(3, 20, n).astype(float),
        "CRSArrTime": to_hhmm(crs_dep + elapsed), "ArrTime": to_hhmm(crs_dep + elapsed + arr_delay),
        "ArrDelay": arr_delay, "ArrDel15": (arr_delay >= 15).astype(float),
        "Cancelled": cancelled.astype(float),
        "CancellationCode": np.where(cancelled, rng.choice(list("ABCD"), n), None),
        "Diverted": diverted.astype(float),
        "CRSElapsedTime": elapsed.astype(float), "AirTime": (elapsed - 25).astype(float),
        "Distance": dist.astype(float),
    })
    late = arr_delay >= 15
    split = rng.dirichlet([2, 1, 2, 0.2, 3], n)
    for i, col in enumerate(["CarrierDelay", "WeatherDelay", "NASDelay", "SecurityDelay", "LateAircraftDelay"]):
        df[col] = np.where(late, np.round(arr_delay * split[:, i]), np.nan)

    # Cancelled / diverted flights have no actual times or delays in BTS
    blank = ["DepTime", "DepDelay", "DepDel15", "TaxiOut", "TaxiIn", "ArrTime", "ArrDelay", "ArrDel15", "AirTime"]
    df.loc[cancelled | diverted, blank] = np.nan
    df.loc[cancelled | diverted, ["CarrierDelay", "WeatherDelay", "NASDelay", "SecurityDelay", "LateAircraftDelay"]] = np.nan

    # Inject a few defects so the cleaning step has something to catch
    df = pd.concat([df, df.sample(50, random_state=1)], ignore_index=True)
    df.loc[df.sample(5, random_state=2).index, "CRSDepTime"] = 2400

    out = ROOT / "data" / "sample" / "sample_flights.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df):,} synthetic rows to {out}")


if __name__ == "__main__":
    main()
