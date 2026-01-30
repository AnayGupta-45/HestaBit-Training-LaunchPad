import pandas as pd
import json
import logging
from pathlib import Path
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

FEATURE_PATH = Path("src/features")
MODEL_PATH = Path("src/models")
DATA_PATH = Path("src/data/processed")
EVAL_PATH = Path("src/evaluation")
LOGS_PATH = Path("src/logs")

EVAL_PATH.mkdir(exist_ok=True)
LOGS_PATH.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOGS_PATH / "error_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_data():
    X_test = pd.read_csv(DATA_PATH / "X_test.csv")
    y_test = pd.read_csv(DATA_PATH / "y_test.csv").squeeze()
    with open(FEATURE_PATH / "feature_list.json") as f:
        features = json.load(f)
    return X_test[features], y_test

def main():
    logger.info("Error analysis started")
    X_test, y_test = load_data()
    model = joblib.load(MODEL_PATH / "best_model.pkl")
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(4, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(EVAL_PATH / "confusion_matrix.png")
    plt.close()
    logger.info("Confusion matrix saved")
    logger.info("Error analysis completed")

if __name__ == "__main__":
    main()
