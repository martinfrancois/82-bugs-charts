#!/usr/bin/env python3
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, MultipleLocator
from pathlib import Path
from datetime import datetime

# ---------- Config ----------
CSV_PATH = Path(sys.argv[1] if len(sys.argv) > 1 else "Bugs.csv")  # CSV path: first command-line argument, Bugs.csv when omitted
START_DATE = datetime(2024, 1, 1)

OUT_MONTHLY = Path("bugs_severity_over_time_monthly.svg")
OUT_QUARTERLY = Path("bugs_severity_over_time_quarterly.svg")

# Colors: Blocker bottom (black), Critical middle (neutral grey), Below Critical top (white)
COLORS = {
    "Blocker": "#000000",
    "Critical": "#8a8a8a",
    "Below Critical": "#ffffff",
}

# Styling
TICK_FONTSIZE = 14
LEGEND_LINEWIDTH = 0.5   # border thickness
TITLE_Y = 0.97           # more padding between title and chart
SIDE_GAP = 0.6          # how much of a bar-width to show beyond first/last bar

# ---------- Helpers ----------
DATE_CANDIDATES = [
    "Date","date","DATE",
    "Timestamp","timestamp","TIMESTAMP",
    "Created","created","CREATED",
    "When","when","WHEN",
    "Logged_At","logged_at","Logged at","LOGGED_AT",
    "Reported","reported","REPORTed",
    "Time","time","TIME",
]

def parse_dateframe_dayfirst(frame: pd.DataFrame) -> pd.Series:
    """Parse a date column with dayfirst=True to avoid ambiguous warnings."""
    for name in DATE_CANDIDATES:
        if name in frame.columns:
            parsed = pd.to_datetime(frame[name], errors="coerce", utc=True, dayfirst=True)
            if parsed.notna().mean() > 0.5:
                return parsed
    # fallback: try all object columns with dayfirst=True
    best_parsed, best_score = None, 0.0
    for col in frame.columns:
        if frame[col].dtype == object:
            parsed = pd.to_datetime(frame[col], errors="coerce", utc=True, dayfirst=True)
            score = parsed.notna().mean()
            if score > best_score:
                best_parsed, best_score = parsed, score
    if best_parsed is None or best_parsed.notna().mean() <= 0.5:
        raise RuntimeError("Could not parse a usable date column with day-first parsing.")
    return best_parsed

def map_three_levels(sev: object) -> str:
    s = "" if pd.isna(sev) else str(sev).strip().lower()
    if "blocker" in s:
        return "Blocker"
    if "critical" in s:
        return "Critical"
    return "Below Critical"

def style_axes(ax: plt.Axes, title: str, is_monthly: bool, label_strings: list[str]) -> None:
    # X labels: vertical, bigger fonts; bold January on monthly
    ax.set_xticks(np.arange(len(label_strings)))
    ax.set_xticklabels(label_strings)
    for label in ax.get_xticklabels():
        label.set_rotation(90)
        label.set_fontsize(TICK_FONTSIZE)
        if is_monthly and label.get_text().endswith("-01"):
            label.set_fontweight("bold")

    # Y axis: 10% steps, percent format, 0..100
    ax.tick_params(axis="y", labelsize=TICK_FONTSIZE)
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_major_formatter(PercentFormatter())
    ax.set_ylim(0, 100)

    # Grid: horizontal dashed only (no vertical gridlines)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Clean spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.set_xlabel("Month", fontsize=15)
    ax.set_ylabel("Percent of Monthly Bugs", fontsize=15)
    plt.suptitle(title, y=TITLE_Y, fontsize=19)

def draw_stacked_100_bars(pct_df: pd.DataFrame, labels: list[str], outfile: Path, title: str, is_monthly: bool) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    order = ["Blocker", "Critical", "Below Critical"]  # bottom -> top
    bottom = np.zeros(len(pct_df))
    x = np.arange(len(pct_df))

    for col in order:
        vals = pct_df.get(col, pd.Series(0, index=pct_df.index)).values
        ax.bar(x, vals, bottom=bottom, color=COLORS[col], edgecolor=None, linewidth=0, label=col)
        bottom += vals

    # Tighter side gaps
    ax.set_xlim(-SIDE_GAP, (len(pct_df) - 1) + SIDE_GAP)

    style_axes(ax, title, is_monthly=is_monthly, label_strings=labels)

    # Legend inside the chart, top-right, with black outline and tick-matched font size
    leg = ax.legend(title="Severity", ncol=1, frameon=True, loc="upper right", prop={"size": TICK_FONTSIZE}, title_fontsize=TICK_FONTSIZE)
    leg.get_frame().set_edgecolor("black")
    leg.get_frame().set_linewidth(LEGEND_LINEWIDTH)
    leg.get_frame().set_facecolor("white")
    leg.get_frame().set_alpha(1.0)

    plt.tight_layout()
    plt.savefig(outfile, format="svg", bbox_inches="tight")
    plt.close(fig)

# ---------- Main ----------
def main():
    # Load
    try:
        df = pd.read_csv(CSV_PATH)
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_PATH, encoding="latin-1")

    # Parse date, convert to naive
    parsed = parse_dateframe_dayfirst(df)
    df["_date"] = parsed.dt.tz_convert(None)

    # Filter from start date
    df = df.loc[df["_date"] >= START_DATE].copy()

    # Map severity to exactly three buckets
    sev_col = next((c for c in ["Severity","severity","SEVERITY","Level","level","Priority","priority"] if c in df.columns), None)
    if sev_col is not None:
        df["_sev3"] = df[sev_col].apply(map_three_levels)
    else:
        df["_sev3"] = "Below Critical"

    # ---------- Monthly ----------
    df["_month"] = df["_date"].dt.to_period("M")
    counts = df.groupby(["_month","_sev3"]).size().unstack(fill_value=0).sort_index()
    # Ensure all 3 columns exist and enforce stack order bottom->top
    for col in ["Below Critical","Critical","Blocker"]:
        if col not in counts.columns:
            counts[col] = 0
    counts = counts[["Blocker","Critical","Below Critical"]]

    totals = counts.sum(axis=1)
    counts = counts.loc[totals > 0]
    pct_monthly = counts.div(counts.sum(axis=1), axis=0) * 100.0

    labels_monthly = pct_monthly.index.astype(str).tolist()
    draw_stacked_100_bars(
        pct_monthly,
        labels_monthly,
        OUT_MONTHLY,
        "Severity Over Time (100% Stacked Bars)",
        is_monthly=True
    )

    # ---------- Quarterly ----------
    df["_quarter"] = df["_date"].dt.to_period("Q")
    counts_q = df.groupby(["_quarter","_sev3"]).size().unstack(fill_value=0).sort_index()
    for col in ["Below Critical","Critical","Blocker"]:
        if col not in counts_q.columns:
            counts_q[col] = 0
    counts_q = counts_q[["Blocker","Critical","Below Critical"]]

    totals_q = counts_q.sum(axis=1)
    counts_q = counts_q.loc[totals_q > 0]
    pct_quarterly = counts_q.div(counts_q.sum(axis=1), axis=0) * 100.0

    labels_quarterly = pct_quarterly.index.astype(str).tolist()
    draw_stacked_100_bars(
        pct_quarterly,
        labels_quarterly,
        OUT_QUARTERLY,
        "Severity Over Time (100% Stacked Bars, Quarterly)",
        is_monthly=False
    )

    print(f"Saved:\n  {OUT_MONTHLY}\n  {OUT_QUARTERLY}")

if __name__ == "__main__":
    main()
