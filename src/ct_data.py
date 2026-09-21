from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = _ROOT / "data" / "raw"
SPECIMEN_PATH = _ROOT / "data" / "reference" / "specimens.csv"
SPECIMENS = pd.read_csv(SPECIMEN_PATH)[
    ["specimen_id", "id_mm", "material", "batch", "notes"]
]

RENAME = {
    "Newtons (N)": "force_N",
    "Line current (A)": "line_current_A",
    "Output Current (uA)": "output_uA",
    "Load (V)": "load_V",
}

EXPECTED = {
    "force_N",
    "line_current_A",
    "output_uA",
    "load_V",
    "test_date",
    "specimen_id",
    "replicate",
}


# helpers


def _resolve_single_file(pattern):
    """Exactly one file matching a glob in RAW_DIR, or raise."""
    matches = list(RAW_DIR.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No file matching {pattern} in {RAW_DIR}")
    if len(matches) > 1:
        raise ValueError(f"Multiple files matching {pattern}: {matches}")
    return matches[0]


def _derive_power(df):
    """Harvested power (mW) from output current (uA) and load (V)."""
    return df["output_uA"] * df["load_V"] * 1e-3


# loaders


def load_ct_data(path):
    """Load one trial CSV into a tidy DataFrame with derived power/force columns."""
    path = Path(path)

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df = df.rename(columns=RENAME)
    df["specimen_id"] = df["specimen_id"].str.strip()
    df["trial_id"] = path.stem.split("_")[1]

    missing = EXPECTED - set(df.columns)
    if missing:
        raise ValueError(f"{path.name}: missing columns {missing}")

    for col in ["force_N", "line_current_A", "output_uA", "load_V", "replicate"]:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"{path.name}: {col} not numeric")

    df = df.merge(
        SPECIMENS, on="specimen_id", how="left", validate="many_to_one", indicator=True
    )
    unregistered = df.loc[df["_merge"] == "left_only", "specimen_id"].unique()
    if len(unregistered):
        raise ValueError(f"{path.name}: specimens not in registry: {unregistered}")
    df = df.drop(columns="_merge")

    df["test_date"] = pd.to_datetime(df["test_date"])
    df["power_mW"] = _derive_power(df)
    df["force_lbf"] = df["force_N"] * 0.224809
    return df


def load_trial(trial_id):
    """Load a trial by id, e.g. load_trial('003'). Globs by id so you don't
    need the date in the filename."""
    return load_ct_data(_resolve_single_file(f"trial_{trial_id}_*.csv"))


def load_benchmarks(benchmark_id):
    """Load one benchmark CSV. No specimen registry or force sweep — just
    current/load/power under a stated clamp method."""
    path = _resolve_single_file(f"benchmark_{benchmark_id}_*.csv")
    df = pd.read_csv(path)

    for col in ["line_current_A", "output_uA", "load_V"]:
        if not pd.api.types.is_numeric_dtype(df[col]) or df[col].isna().any():
            raise ValueError(f"{path.name}: {col} must be numeric and non-null")
    if df["clamp_method"].isna().any():
        raise ValueError(f"{path.name}: clamp_method must be non-null")

    df["benchmark_id"] = benchmark_id
    df["power_mW"] = _derive_power(df)
    return df
