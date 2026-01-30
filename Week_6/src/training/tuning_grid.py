import pandas as pd
import json
import logging
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold

FEATURE_PATH = Path("src/features")
DATA_PATH = Path("src/data/processed")
TUNING_PATH = Path("src/tuning")
LOGS_PATH = Path("src/logs")

TUNING_PATH.mkdir(exist_ok=True)
LOGS_PATH.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOGS_PATH / "tuning_grid.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_data():
    X = pd.read_csv(DATA_PATH / "X_train.csv")
    y = pd.read_csv(DATA_PATH / "y_train.csv").squeeze()

    with open(FEATURE_PATH / "feature_list.json") as f:
        features = json.load(f)
    X = X[features]
    return X, y

def main():
    logger.info("GridSearch tuning started (Logistic Regression)")

    X, y = load_data()

    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        solver="liblinear"
    )
    param_grid = {
        "penalty": ["l1", "l2"],
        "C": [0.01, 0.1, 1, 10]
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid = GridSearchCV(
        model,
        param_grid,
        scoring="roc_auc",
        cv=cv,
        n_jobs=-1
    )
    grid.fit(X, y)
    results = {
        "best_params": grid.best_params_,
        "best_roc_auc": grid.best_score_
    }
    with open(TUNING_PATH / "grid_results.json", "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Best ROC-AUC: {grid.best_score_:.4f}")
    logger.info(f"Best params: {grid.best_params_}")
    logger.info("GridSearch tuning completed")


if __name__ == "__main__":
    main()
