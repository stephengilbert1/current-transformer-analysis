# imports

import matplotlib.pyplot as plt
import pandas as pd
from ct_data import load_trial
from matplotlib.lines import Line2D

# constants

FORCE_UNITS = {
    "N":   ("force_N",   "Force (N)"),
    "lbf": ("force_lbf", "Force (lbf)"),
}

_SPECIMEN_COLORS = {}
_CYCLE = plt.get_cmap("tab10").colors

# color

def specimen_color(specimen):
    """Colour for a specimen. Assigned the first time it's seen, in load
    order, and remembered for the rest of the session. Cycle wraps past 10."""
    if specimen not in _SPECIMEN_COLORS:
        _SPECIMEN_COLORS[specimen] = _CYCLE[len(_SPECIMEN_COLORS) % len(_CYCLE)]
    return _SPECIMEN_COLORS[specimen]

def _resolve_colors(dfs):
    """One colour per CT sample"""
    return [specimen_color(df["specimen_id"].iloc[0]) for df in dfs]

# data shaping

def load_sweeps(trial_id):
    """One file → list of ((specimen_id, replicate), sweep_df), one per specimen×replicate sweep."""
    df = load_trial(trial_id)
    return list(df.groupby(["specimen_id", "replicate"], sort=True))

def load_all_sweeps(trial_ids):
    """Explode several trials into one flat list of sweeps, globally sorted."""
    sweeps = []
    for tid in trial_ids:
        sweeps.extend(load_sweeps(tid))
    sweeps.sort(key=lambda item: item[0])
    return sweeps

# figure text

def condition_subtitle(df):
    current_start = df["line_current_A"].iloc[0]
    current_end   = df["line_current_A"].iloc[-1]
    load_min      = df["load_V"].min()
    load_max      = df["load_V"].max()
    ct            = df["specimen_id"].iloc[0]
    return (f"Line Current = {current_start}–{current_end} A   |   "
            f"Load = {load_min}–{load_max} V   |   CT = {ct}")

def comparison_subtitle(dfs):
    """Full current/voltage envelope across all trials; CT type only if shared."""
    i_min = min(df["line_current_A"].min() for df in dfs)
    i_max = max(df["line_current_A"].max() for df in dfs)
    v_min = min(df["load_V"].min() for df in dfs)
    v_max = max(df["load_V"].max() for df in dfs)

    parts = [
        f"Line Current = {i_min}–{i_max} A",
        f"Load = {v_min}–{v_max} V",
    ]

    cts = {df["specimen_id"].iloc[0] for df in dfs}
    if len(cts) == 1:
        parts.append(f"CT = {next(iter(cts))}")

    return "   |   ".join(parts)

def date_span_annotation(dfs):
    tids = sorted({df["trial_id"].iloc[0] for df in dfs})
    dates = sorted(df["test_date"].iloc[0].strftime("%Y-%m-%d") for df in dfs)

    if len(tids) == 1:
        trial_part = f"Trial {tids[0]}"
    else:
        trial_part = f"Trials {', '.join(tids)}"

    if dates[0] == dates[-1]:
        date_part = dates[0]
    else:
        date_part = f"{dates[0]} to {dates[-1]}"

    return f"{trial_part} · {date_part}"

def source_annotation(df):
    tid  = df["trial_id"].iloc[0]
    date = df["test_date"].iloc[0].strftime("%Y-%m-%d")
    return f"Trial {tid} · {date}"

# Single trial plot

def plot_trial(df, y, force_unit="N", ylabel=None):
    col, xlabel = FORCE_UNITS[force_unit]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df[col], df[y], marker="o", markersize=3, linewidth=1.5)

    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel or y, rotation=0, ha="right", va="center")
    ax.yaxis.set_label_coords(-0.02, 1.02)

    ax.grid(True, alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return fig, ax

# Comparison plots

def compare_sweeps(trial_ids, xlim=None, y="power_mW"):
    """Compare sweeps across one or more trials. Each sweep (specimen×replicate)
    draws as one line, coloured by specimen."""
    sweeps = load_all_sweeps(trial_ids)
    frames = [df for _key, df in sweeps]

    fig, ax = plt.subplots(figsize=(8, 5))
    _draw_comparison(ax, frames, xlim=xlim, y=y)
    _add_sweep_legend(ax, sweeps)
    ax.set_title(comparison_subtitle(frames), fontsize=9)
    ax.set_ylabel("Power (mW)", rotation=0, ha="right", va="center")
    ax.yaxis.set_label_coords(-0.02, 1.02)
    fig.text(0.02, -0.02, date_span_annotation(frames), ha="left", fontsize=8, color="gray")
    return fig, ax

def compare_sweeps_dual(trial_ids, zoom=(0, 10), y="power_mW"):
    """Two-panel sweep comparison: full range and zoomed, side by side."""
    sweeps = load_all_sweeps(trial_ids)
    frames = [df for _key, df in sweeps]
    

    fig, (ax_full, ax_zoom) = plt.subplots(1, 2, figsize=(13, 5))
    _draw_comparison(ax_full, frames, xlim=None, y=y)
    _draw_comparison(ax_zoom, frames, xlim=zoom, y=y)

    ax_full.set_title(comparison_subtitle(frames), fontsize=9)
    ax_zoom.set_title(f"Zoom {zoom[0]}–{zoom[1]} N", fontsize=10)
    _add_sweep_legend(ax_full, sweeps)
    ax_full.set_ylabel("Power (mW)", rotation=0, ha="right", va="center")
    fig.text(0.02, -0.02, date_span_annotation(frames), ha="left", fontsize=8, color="gray")
    return fig, (ax_full, ax_zoom)

def _draw_comparison(ax, dfs, xlim=None, y="power_mW"):
    colors = _resolve_colors(dfs)
    for df, color in zip(dfs, colors):
        ax.plot(
            df["force_N"], df[y],
            marker="o", color=color,
            markersize=3, linewidth=1.5,
        )

    if xlim is not None:
        ax.set_xlim(*xlim)
        visible = pd.concat([df.loc[df["force_N"].between(*xlim), y] for df in dfs])
        ax.set_ylim(visible.min(), visible.max() * 1.1)

    if xlim is None:
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)

    ax.set_xlabel("Force (N)")
    ax.grid(True, alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)



def _add_sweep_legend(ax, sweeps):
    """Legend names specimens, but only when more than one is present.
    A single-specimen chart omits it — colour is constant, so a legend
    would just repeat the same entry."""
    specimens = list(dict.fromkeys(s for (s, _r), _df in sweeps))
    if len(specimens) <= 1:
        return                      # nothing to distinguish; skip the legend
    handles = [Line2D([0], [0], color=specimen_color(s), marker="o",
                      linewidth=1.5, label=s) for s in specimens]
    ax.legend(handles=handles, title="Specimen", fontsize=8)



