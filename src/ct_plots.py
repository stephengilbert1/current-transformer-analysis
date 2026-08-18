import matplotlib.pyplot as plt

FORCE_UNITS = {
    "N":   ("force_N",   "Force (N)"),
    "lbf": ("force_lbf", "Force (lbf)"),
}

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