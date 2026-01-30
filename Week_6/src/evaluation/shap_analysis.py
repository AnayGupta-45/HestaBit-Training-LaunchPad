import pandas as pd
import json
import logging
from pathlib import Path
import joblib
import shap
import matplotlib.pyplot as plt

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
        logging.FileHandler(LOGS_PATH / "shap.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_data():
    X_test = pd.read_csv(DATA_PATH / "X_test.csv")

    with open(FEATURE_PATH / "feature_list.json") as f:
        features = json.load(f)

    return X_test[features]

def load_model():
    return joblib.load(MODEL_PATH / "best_model.pkl")

def shap_summary(model, X):
    masker = shap.maskers.Independent(X)
    explainer = shap.LinearExplainer(
        model,
        masker
    )
    shap_values = explainer(X)
    plt.figure()
    shap.summary_plot(shap_values.values, X, show=False)
    plt.tight_layout()
    plt.savefig(EVAL_PATH / "shap_summary.png")
    plt.close()
    logger.info("SHAP summary plot saved")

def main():
    logger.info("SHAP explainability started")
    X_test = load_data()
    model = load_model()
    shap_summary(model, X_test)
    logger.info("SHAP explainability completed")

if __name__ == "__main__":
    main()
