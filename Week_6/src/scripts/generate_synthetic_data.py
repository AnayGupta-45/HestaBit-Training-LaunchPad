import pandas as pd

TRAIN_PATH = "src/data/processed/X_train.csv"
OUT_PATH = "src/data/processed/X_synthetic.csv"

df = pd.read_csv(TRAIN_PATH)

synthetic_df = df.sample(
    n=200,
    replace=True,
    random_state=42
)

synthetic_df.to_csv(OUT_PATH, index=False)

print("Synthetic data generated:", OUT_PATH)
