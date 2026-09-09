from pathlib import Path
import pandas as pd
RAW_DIR = Path("../data/raw")

RENAME = {
    "Newtons (N)": "force_N",
    "Line current (A)": "line_current_A",
    "Output Current (uA)": "output_uA",
    "Load (V)": "load_V",
}

EXPECTED = {
    "force_N", "line_current_A", "output_uA", "load_V",
    "test_date", "specimen_id", "replicate",
}



def load_ct_data(path):
    """Load one trial CSV into a tidy DataFrame with derived power/force columns."""
    path = Path(path)

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df = df.rename(columns=RENAME)

    df["trial_id"] = path.stem.split("_")[1]   # provenance tag from filename

    # --- validate ---
    missing = EXPECTED - set(df.columns)
    assert not missing, f"{path.name}: missing columns {missing}"

    for col in ["force_N", "line_current_A", "output_uA", "load_V", "replicate"]:
        assert pd.api.types.is_numeric_dtype(df[col]), f"{path.name}: {col} not numeric"

    # --- derived columns  ---
    df["test_date"] = pd.to_datetime(df["test_date"])
    df["power_mW"] = (df["output_uA"] * 1e-3) * df["load_V"]
    df["force_lbf"] = df["force_N"] * 0.224809

    return df

def load_trial(trial_id):
    """Load a trial by id, e.g. load_trial('003'). Finds the file by glob so
    you don't have to know the date in the filename."""
    matches = list(RAW_DIR.glob(f"trial_{trial_id}_*.csv"))
    if not matches:
        raise FileNotFoundError(f"No file for trial {trial_id} in {RAW_DIR}")
    if len(matches) > 1:
        raise ValueError(f"Multiple files for trial {trial_id}: {matches}")
    return load_ct_data(matches[0])


def load_benchmarks(benchmark_id):
    matches = list(RAW_DIR.glob(f"benchmark_{benchmark_id}_*.csv"))
    if len(matches) != 1:
        raise FileNotFoundError(f"benchmark_{benchmark_id}: expected one file, found {len(matches)}")
    df = pd.read_csv(matches[0])

    measure_cols = ["line_current_A", "output_uA", "load_V"]
    for c in measure_cols:
        if not pd.api.types.is_numeric_dtype(df[c]) or df[c].isna().any():
            raise ValueError(f"benchmark_{benchmark_id}: {c} must be numeric and non-null")
    if df["clamp_method"].isna().any():
        raise ValueError(f"benchmark_{benchmark_id}: clamp_method must be non-null")

    df["benchmark_id"] = benchmark_id
    df["power_mW"] = df["output_uA"] * df["load_V"] * 1e-3
    return df