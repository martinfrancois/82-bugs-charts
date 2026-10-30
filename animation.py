#!/usr/bin/env python3
"""
Animate monthly counts by bug type and the most frequent bug subtypes.

Horizontal black bars transition between months, with the month label above
the chart and a left margin sized to fit the category labels.
"""

from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from bugs_csv import csv_path


# --------------- Config ---------------

CSV_PATH = csv_path()
OUT_DIR = Path("out")
START_MONTH = "2024-01-01"
STEPS_PER_MONTH = 10
FPS = 8
TOP_N_SUBTYPES = 12

# Font sizes inspired by your static chart
TITLE_FONTSIZE = 20
LABEL_FONTSIZE = 17
TICK_FONTSIZE = 16
MONTH_FONTSIZE = 26

# Extra padding on the left margin beyond label width, in inches
LEFT_PAD_IN = 0.40


# --------------- Robust date parsing ---------------

def parse_dates_strict(series: pd.Series) -> pd.Series:
    """
    Parse a date column robustly without ambiguous format warnings.
    Supports:
      ISO: YYYY-MM-DD
      Slash: DD/MM/YYYY
      Dots:  DD.MM.YYYY
    Fallback uses dayfirst=True and keeps UTC.
    """
    s = series.astype(str).str.strip()
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns, UTC]")

    m = s.str.match(r"^\d{4}-\d{2}-\d{2}$")
    if m.any():
        out.loc[m] = pd.to_datetime(s[m], format="%Y-%m-%d", utc=True)

    m = s.str.match(r"^\d{1,2}/\d{1,2}/\d{4}$")
    if m.any():
        out.loc[m] = pd.to_datetime(s[m], format="%d/%m/%Y", utc=True)

    m = s.str.match(r"^\d{1,2}\.\d{1,2}\.\d{4}$")
    if m.any():
        out.loc[m] = pd.to_datetime(s[m], format="%d.%m.%Y", utc=True)

    rem = out.isna()
    if rem.any():
        out.loc[rem] = pd.to_datetime(s[rem], errors="coerce", utc=True, dayfirst=True)

    return out


# --------------- Data prep ---------------

def load_data(csv_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(csv_path)
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="latin-1")

    df["_parsed_date"] = parse_dates_strict(df["Date"])
    df["_date"] = df["_parsed_date"].dt.tz_convert(None)
    df["_month"] = df["_date"].dt.to_period("M").dt.to_timestamp()
    df = df[df["_month"] >= pd.Timestamp(START_MONTH)].copy()
    return df


def prepare_monthly(
        df: pd.DataFrame,
        col: str,
        top_n: Optional[int] = None
) -> Tuple[pd.DataFrame, List[str], pd.DatetimeIndex]:
    df = df.copy()
    df[col] = df[col].fillna("Unspecified").astype(str)

    monthly = df.groupby(["_month", col]).size().unstack(fill_value=0).sort_index()

    months = pd.period_range(
        monthly.index.min().to_period("M"),
        monthly.index.max().to_period("M"),
        freq="M",
    ).to_timestamp()
    monthly = monthly.reindex(index=months, fill_value=0)

    totals = monthly.sum(axis=0).sort_values(ascending=False)

    if top_n is not None:
        keep = totals.head(top_n).index.tolist()
        monthly = monthly.reindex(columns=keep, fill_value=0)
        order = keep
    else:
        order = totals.index.tolist()

    return monthly, order, months


# --------------- Animation ---------------

def _ensure_left_margin_for_labels(fig: plt.Figure, ax: plt.Axes) -> None:
    """
    Measure y tick label widths and expand the left margin so labels are not clipped.
    """
    # Force a draw so text extents are available
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    widths_px = []
    for t in ax.get_yticklabels():
        if not t.get_text():
            continue
        bbox = t.get_window_extent(renderer=renderer)
        widths_px.append(bbox.width)

    if not widths_px:
        return

    max_w_px = max(widths_px)
    max_w_in = max_w_px / fig.dpi
    left_in = max_w_in + LEFT_PAD_IN
    fig_w_in = fig.get_size_inches()[0]
    left_frac = min(0.9, max(0.05, left_in / fig_w_in))  # keep sane bounds

    # Apply and redraw to lock the layout before animation frames render
    fig.subplots_adjust(left=left_frac)
    fig.canvas.draw()


def animate_hbar(
        monthly: pd.DataFrame,
        order: List[str],
        months: pd.DatetimeIndex,
        title: str,
        outfile: Path,
        steps_per_month: int = STEPS_PER_MONTH,
        fps: int = FPS,
) -> None:
    monthly = monthly.reindex(columns=order, fill_value=0)
    M = monthly.to_numpy(dtype=float)
    n_months, n_cats = M.shape

    # Frame plan: exact first month, then tweens into each next month
    frames = [(0, 1.0)]
    for i in range(n_months - 1):
        for s in range(1, steps_per_month + 1):
            frames.append((i, s / steps_per_month))

    xmax = float(M.max()) if np.isfinite(M.max()) and M.max() > 0 else 1.0

    fig, ax = plt.subplots(figsize=(12, max(6, n_cats * 0.5)))
    y = np.arange(n_cats)

    bars = ax.barh(y, M[0], color="black")
    ax.set_yticks(y)
    ax.set_yticklabels(order, fontsize=TICK_FONTSIZE)
    ax.set_xlabel("Count", fontsize=LABEL_FONTSIZE)
    ax.set_xlim(0, xmax * 1.1)
    ax.set_title(title, fontsize=TITLE_FONTSIZE)
    ax.tick_params(axis="x", labelsize=TICK_FONTSIZE)
    ax.tick_params(axis="y", length=0)  # hide y tick marks
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Month label OUTSIDE the chart: figure coordinates, top left
    month_text = fig.text(
        0.01, 0.98, months[0].strftime("%Y-%m"),
        ha="left", va="top",
        fontsize=MONTH_FONTSIZE, fontweight="bold",
        transform=fig.transFigure,
    )

    # Expand left margin based on real label widths so nothing gets cut off
    _ensure_left_margin_for_labels(fig, ax)

    def interp(i: int, t: float) -> np.ndarray:
        if i >= n_months - 1:
            return M[i]
        return (1 - t) * M[i] + t * M[i + 1]

    def update(frame_idx: int):
        i, t = frames[frame_idx]
        vals = interp(i, t)
        for rect, v in zip(bars, vals):
            rect.set_width(v)
        target = months[i] if (i == 0 and t < 1.0) else months[min(i + 1, n_months - 1)]
        month_text.set_text(target.strftime("%Y-%m"))
        return (*bars, month_text)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    anim = FuncAnimation(fig, update, frames=len(frames), interval=int(1000 / fps), blit=False, repeat=False)
    anim.save(str(outfile), writer=PillowWriter(fps=fps))
    plt.close(fig)


# --------------- Main ---------------

def main():
    df = load_data(CSV_PATH)
    if df.empty:
        raise SystemExit(f"No rows on or after {START_MONTH}. Nothing to animate.")

    # Types
    types_monthly, type_order, type_months = prepare_monthly(df, "Type of Bug", top_n=None)
    animate_hbar(
        types_monthly,
        type_order,
        type_months,
        "Bugs per Month by Type",
        OUT_DIR / "bugs_types_transition_hbar.gif",
        )

    # Subtypes
    subs_monthly, sub_order, sub_months = prepare_monthly(df, "Subtype", top_n=TOP_N_SUBTYPES)
    animate_hbar(
        subs_monthly,
        sub_order,
        sub_months,
        f"Bugs per Month by Subtype (Top {len(sub_order)})",
        OUT_DIR / "bugs_subtypes_transition_hbar.gif",
        )


if __name__ == "__main__":
    main()
