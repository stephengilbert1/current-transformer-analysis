from pathlib import Path
import pandas as pd
RAW_DIR = Path("../data/raw")

RENAME = {
    "Newtons (N)": "force_N",
    "Line current (A)": "line_current_A",
    "Min Power (W)": "power_min_W",
    "Max Power (W)": "power_max_W",
    "Output Current (uA)" : "output_uA",
    "Load (V)" : "load_V"
    
}
EXPECTED = set(RENAME.values())

def load_ct_data(path):
    """Load one trial CSV into a tidy DataFrame, stamped with trial_id and date."""
    path = Path(path)

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df = df.rename(columns=RENAME)

    parts = Path(path).stem.split("_")
    df["trial_id"]=parts[1]
    df["date"]=pd.to_datetime(parts[2])

    # --- derived columns (not measurements) ---
    df["power_mW"] = (df["output_uA"] * 1e-3) * df["load_V"]
    df["force_lbf"] = df["force_N"] * 0.224809

    missing = EXPECTED - set(df.columns)
    assert not missing, f"{path.name}: missing columns {missing}"

    for col in ["force_N", "line_current_A", "power_min_W", "power_max_W"]:
        assert pd.api.types.is_numeric_dtype(df[col]), f"{path.name}: {col} not numeric"

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