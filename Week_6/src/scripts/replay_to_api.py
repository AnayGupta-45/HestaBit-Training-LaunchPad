import pandas as pd
import requests
from time import sleep

API_URL = "http://127.0.0.1:8000/predict"
DATA_PATH = "src/data/processed/X_synthetic.csv"

df = pd.read_csv(DATA_PATH)

for _, row in df.iterrows():
    payload = row.to_dict()
    requests.post(API_URL, json=payload)
    sleep(0.05)

print("Replay completed")
