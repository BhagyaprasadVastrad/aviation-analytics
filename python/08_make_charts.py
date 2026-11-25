"""Create the project charts from the SQL result CSVs (fast; no warehouse needed).

Usage:
    python python/08_make_charts.py

Reads:  data/processed/results/*.csv   (written by 03_run_sql_analysis.py)
Writes: documentation/charts/*.png
"""
import calendar
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "data" / "processed" / "results"
OUT = ROOT / "documentation" / "charts"
OUT.mkdir(parents=True, exist_ok=True)

MONTH_COLORS = {2: "#4C78A8", 6: "#E45756", 9: "#59A14F", 12: "#F28E2B"}
INK, GRID = "#2B2B2B", "#E6E6E6"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": "#999999", "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK, "axes.titleweight": "bold", "axes.titlesize": 13})


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(RES / f"{name}.csv")


def mname(m: int) -> str:
    return calendar.month_abbr[int(m)]


def save(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=160, facecolor="white")
    plt.close(fig)
    print(f"Wrote {OUT / name}")


def heatmap(ax, data: pd.DataFrame, cmap: str, fmt: str = "{:.1f}") -> None:
    im = ax.imshow(data.values, cmap=cmap, aspect="auto")
    ax.set_xticks(range(data.shape[1]), labels=data.columns)
    ax.set_yticks(range(data.shape[0]), labels=data.index)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            v = data.values[i, j]
            r, g, b, _ = im.cmap(im.norm(v))
            lum = 0.299 * r + 0.587 * g + 0.114 * b  # perceived brightness of this cell
            ax.text(j, i, fmt.format(v), ha="center", va="center", fontsize=9,
                    color="white" if lum < 0.5 else INK)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)



def hour_by_month() -> None:
    df = load("05_route_analysis__6")
    df = df[df["crs_dep_hour"] >= 5]
    fig, ax = plt.subplots(figsize=(9, 5))
    for m, g in df.groupby("month"):
        ax.plot(g["crs_dep_hour"], g["dep_delay_rate_pct"], marker="o", ms=4, lw=2.2,
                color=MONTH_COLORS.get(int(m), "#777"), label=mname(m))
    ax.set_title("Delays build through the day in every season")
    ax.set_xlabel("Scheduled departure hour")
    ax.set_ylabel("% of flights departing 15+ minutes late")
    ax.set_xticks(range(5, 24, 2))
    ax.grid(axis="y", color=GRID)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(title="Month", frameon=False)
    save(fig, "01_delay_buildup_by_hour.png")


def monthly_scorecard() -> None:
    df = load("05_route_analysis__7").sort_values("month")
    labels = [mname(m) for m in df["month"]]
    colors = [MONTH_COLORS.get(int(m), "#777") for m in df["month"]]
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.2))
    panels = [("on_time_pct", "On-time arrival (%)", "{:.1f}"), ("dep_delay_rate_pct", "Departures 15+ min late (%)", "{:.1f}"),
              ("cancellation_rate_pct", "Cancellation rate (%)", "{:.2f}")]
    for ax, (col, title, fmt) in zip(axes, panels):
        bars = ax.bar(labels, df[col], color=colors, width=0.62)
        for b, v in zip(bars, df[col]):
            ax.text(b.get_x() + b.get_width() / 2, v, fmt.format(v), ha="center", va="bottom", fontsize=9, color=INK)
        ax.set_title(title, fontsize=11)
        ax.set_ylim(0, df[col].max() * 1.18)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.set_yticks([])
    fig.suptitle("June is the hardest month; September and February the easiest", fontweight="bold", fontsize=13)
    save(fig, "02_monthly_scorecard.png")


def airline_heatmap() -> None:
    df = load("03_airline_analysis__2")
    df["m"] = df["month"].map(mname)
    order = [mname(m) for m in sorted(df["month"].unique())]
    pv = df.pivot_table(index="airline_name", columns="m", values="on_time_pct")[order]
    pv = pv.loc[pv.mean(axis=1).sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(7.5, 7))
    heatmap(ax, pv, "RdYlGn")
    ax.set_title("Airline on-time arrival % by month\n(sorted by four-month average)", fontsize=12)
    save(fig, "03_airline_ontime_by_month.png")


def hub_heatmap() -> None:
    df = load("04_airport_analysis__5")
    df["m"] = df["month"].map(mname)
    order = [mname(m) for m in sorted(df["month"].unique())]
    pv = df.pivot_table(index="origin_airport", columns="m", values="dep_delay_rate_pct")[order]
    pv = pv.loc[pv.max(axis=1).sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(6.5, 7))
    heatmap(ax, pv, "YlOrRd")
    ax.set_title("Busiest 15 airports: % of departures 15+ min late\n(sorted by worst month)", fontsize=12)
    save(fig, "04_hub_delay_by_month.png")


def delay_causes() -> None:
    df = load("06_delay_causes_analysis__1").sort_values("pct_of_delay_minutes")
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(df["cause"], df["pct_of_delay_minutes"], color="#4C78A8")
    for b, v in zip(bars, df["pct_of_delay_minutes"]):
        ax.text(v + 0.5, b.get_y() + b.get_height() / 2, f"{v:.1f}%", va="center", fontsize=10, color=INK)
    ax.set_title("Late-arriving aircraft cause the most delay minutes")
    ax.set_xlabel("Share of delay minutes (flights arriving 15+ min late)")
    ax.set_xlim(0, df["pct_of_delay_minutes"].max() * 1.15)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "05_delay_causes.png")


def propagation() -> None:
    df = load("06_delay_causes_analysis__5").sort_values("inbound_status")
    labels = ["Early", "On time", "15-59 min late", "60+ min late"][: len(df)]
    fig, ax = plt.subplots(figsize=(8, 4.4))
    bars = ax.bar(labels, df["next_dep_delay_rate_pct"], color=["#59A14F", "#9CBF4F", "#F28E2B", "#E45756"][: len(df)], width=0.62)
    for b, v, d in zip(bars, df["next_dep_delay_rate_pct"], df["avg_next_dep_delay_min"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.1f}%\n(avg {d:.0f} min)", ha="center", fontsize=9.5, color=INK)
    ax.set_title("Late inbound aircraft are followed by late departures")
    ax.set_xlabel("How the same aircraft's previous flight arrived")
    ax.set_ylabel("% of next departures 15+ min late")
    ax.set_ylim(0, df["next_dep_delay_rate_pct"].max() * 1.25)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "06_late_aircraft_propagation.png")


def weekday() -> None:
    df = load("05_route_analysis__2").sort_values("day_of_week")
    fig, ax = plt.subplots(figsize=(8, 4))
    vals = df["dep_delay_rate_pct"]
    colors = ["#E45756" if v == vals.max() else ("#59A14F" if v == vals.min() else "#8FA9C9") for v in vals]
    bars = ax.bar(df["day_name"].str[:3], vals, color=colors, width=0.62)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.3, f"{v:.1f}%", ha="center", fontsize=9.5, color=INK)
    ax.set_title("Sunday, Friday and Saturday run late most often")
    ax.set_ylabel("% of departures 15+ min late")
    ax.set_ylim(0, vals.max() * 1.18)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "07_weekday_delay_rate.png")


def main() -> None:
    for fn in (hour_by_month, monthly_scorecard, airline_heatmap, hub_heatmap, delay_causes, propagation, weekday):
        fn()


if __name__ == "__main__":
    main()
