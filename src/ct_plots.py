import matplotlib.pyplot as plt
import pandas as pd
from ct_data import load_trial


FORCE_UNITS = {
    "N":   ("force_N",   "Force (N)"),
    "lbf": ("force_lbf", "Force (lbf)"),
}

MARKERS = ["o", "s", "^", "*", "D", "v"]

def plot_trial(df, y, force_unit="N", ylabel=None):
    col, xlabel = FORCE_UNITS[force_unit]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df[col], df[y], marker="o", markersize=5, linewidth=1.5)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel or y, rotation=0, ha="right", va="center")
    ax.yaxis.set_label_coords(-0.02, 1.02)

    ax.grid(True, alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return fig, ax

def condition_subtitle(df):
    current_start = df["line_current_A"].iloc[0]
    current_end   = df["line_current_A"].iloc[-1]
    load_min      = df["load_V"].min()
    load_max      = df["load_V"].max()
    ct            = df["ct"].iloc[0]
    return (f"Line Current = {current_start}–{current_end} A   |   "
            f"Load = {load_min}–{load_max} V   |   CT = {ct}")

def date_span_annotation(dfs):
    dates = sorted(df["date"].iloc[0].strftime("%Y-%m-%d") for df in dfs)
    tids  = [df["trial_id"].iloc[0] for df in dfs]
    return f"Trials {tids[0]}–{tids[-1]} · {dates[0]} to {dates[-1]}"

def source_annotation(df):
    tid  = df["trial_id"].iloc[0]
    date = df["date"].iloc[0].strftime("%Y-%m-%d")
    ct   = df["ct"].iloc[0]
    return f"Trial {tid} · {date} · {ct}"

def _draw_comparison(ax, dfs, markers, xlim=None, y="power_mW"):
    """Draw a multi-trial comparison onto an existing axes.
    The private helper — does the plotting, owns no figure."""
    for df, mk in zip(dfs, markers):
        ax.plot(df["force_N"], df[y], marker=mk, markersize=5, linewidth=1.5,
                label=f"Trial {df['trial_id'].iloc[0]} — {df['ct'].iloc[0]}")

    if xlim is not None:
        ax.set_xlim(*xlim)
        visible = pd.concat([df.loc[df["force_N"].between(*xlim), y] for df in dfs])
        ax.set_ylim(visible.min(), visible.max() * 1.1)

    ax.set_xlabel("Force (N)")
    ax.grid(True, alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend()

def compare_trials(trial_ids, xlim=None, y="power_mW"):
    """Single-panel comparison. Full range, or zoomed if xlim given."""
    dfs = [load_trial(tid) for tid in trial_ids]

    fig, ax = plt.subplots(figsize=(8, 5))
    _draw_comparison(ax, dfs, MARKERS, xlim=xlim, y=y)

    ax.set_ylabel("Power (mW)", rotation=0, ha="right", va="center")
    ax.yaxis.set_label_coords(-0.02, 1.02)
    fig.text(0.02, -0.02, date_span_annotation(dfs), ha="left", fontsize=8, color="gray")
    return fig, ax


def compare_trials_dual(trial_ids, zoom=(0, 10), y="power_mW"):
    """Two-panel comparison: full range and zoomed, side by side."""
    dfs = [load_trial(tid) for tid in trial_ids]

    fig, (ax_full, ax_zoom) = plt.subplots(1, 2, figsize=(13, 5))
    _draw_comparison(ax_full, dfs, MARKERS, xlim=None, y=y)
    _draw_comparison(ax_zoom, dfs, MARKERS, xlim=zoom, y=y)

    ax_full.set_title("Full range", fontsize=10)
    ax_zoom.set_title(f"Zoom {zoom[0]}–{zoom[1]} N", fontsize=10)
    ax_full.set_ylabel("Power (mW)", rotation=0, ha="right", va="center")
    fig.text(0.02, -0.02, date_span_annotation(dfs), ha="left", fontsize=8, color="gray")
    return fig, (ax_full, ax_zoom)