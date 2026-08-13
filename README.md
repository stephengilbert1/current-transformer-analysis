# current-transformer-analysis

Reproducible pipeline for loading, processing, and charting current
transformer (CT) test data including force, output current and power across trials.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Raw test data lives in `data/raw/`, one CSV per trial
(`trial_003_2026-08-12.csv`). Load and plot a trial from a notebook:

```python
from ct_data import load_trial
from ct_plots import plot_trial

df = load_trial("003")
fig, ax = plot_trial(df, "force_lbf", "power_mW",
                     xlabel="Force (lbf)", ylabel="Power (mW)")
```

## Structure

- `data/raw/` — raw trial CSVs (immutable)
- `src/ct_data.py` — loading, cleaning, derived columns
- `src/ct_plots.py` — reusable styled plotting
- `notebooks/` — per-analysis exploration
- `figures/` — generated charts