import pandas as pd
from scipy.stats import ks_2samp
from pathlib import Path
import json

TRAIN_PATH = Path("src/data/processed/X_train.csv")
LOG_PATH = Path("src/logs/prediction_logs.csv")
FEATURE_PATH = Path("src/features/feature_list.json")

P_VALUE_THRESHOLD = 0.01
MIN_SAMPLES = 100

def run_drift_check():
    if not LOG_PATH.exists():
        print("No prediction logs found")
        return

    with open(FEATURE_PATH) as f:
        FEATURES = json.load(f)

    train_df = pd.read_csv(TRAIN_PATH)[FEATURES]
    logs_df = pd.read_csv(LOG_PATH)

    recent_df = logs_df[FEATURES].dropna()

    if len(recent_df) < MIN_SAMPLES:
        print("Not enough data for drift detection")
        return

    feature_severity = {}
    drifted = []

    for col in FEATURES:
        _, p = ks_2samp(
            train_df[col].dropna(),
            recent_df[col].dropna()
        )

        if p < 0.001:
            feature_severity[col] = "SEVERE"
            drifted.append(col)
        elif p < 0.01:
            feature_severity[col] = "MODERATE"
            drifted.append(col)
        elif p < 0.05:
            feature_severity[col] = "MILD"

    drift_ratio = len(drifted) / len(FEATURES)

    if drift_ratio == 0:
        system_severity = "NO DRIFT"
    elif drift_ratio <= 0.2:
        system_severity = "MILD DRIFT"
    elif drift_ratio <= 0.4:
        system_severity = "MODERATE DRIFT"
    else:
        system_severity = "SEVERE DRIFT"

    print(f"System Drift Severity: {system_severity}")
    print(f"Drifted Features: {len(drifted)} / {len(FEATURES)}")

    for f in drifted:
        print(f"- {f}: {feature_severity[f]}")

if __name__ == "__main__":
    run_drift_check()
