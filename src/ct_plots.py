import matplotlib.pyplot as plt

def plot_trial(df, x, y, xlabel=None, ylabel=None):
    """Plot y vs x with house style. Returns (fig, ax); caller sets titles."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df[x], df[y], marker="o", markersize=5, linewidth=1.5)

    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or y, rotation=0, ha="right", va="center")
    ax.yaxis.set_label_coords(-0.02, 1.02)

    ax.grid(True, alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return fig, ax

def condition_subtitle(df):
    line, load, ct = df["line_current_A"].iloc[0], df["load_V"].iloc[0], df["ct"].iloc[0]
    return f"Line Current = {line} A   |   Load = {load} V   |   CT = {ct}"