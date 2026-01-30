import pandas as pd
import json
import logging
from pathlib import Path

import optuna
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

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
        logging.FileHandler(LOGS_PATH / "tuning_optuna.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_data():
    X = pd.read_csv(DATA_PATH / "X_train.csv")
    y = pd.read_csv(DATA_PATH / "y_train.csv").squeeze()
    with open(FEATURE_PATH / "feature_list.json") as f:
        features = json.load(f)
    return X[features], y

def objective(trial, X, y):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 400),
        "max_depth": trial.suggest_int("max_depth", 3, 6),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "eval_metric": "logloss",
        "random_state": 42
    }
    model = XGBClassifier(**params)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = []
    for train_idx, val_idx in cv.split(X, y):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        model.fit(X_train, y_train)
        preds = model.predict_proba(X_val)[:, 1]
        scores.append(roc_auc_score(y_val, preds))
    return sum(scores) / len(scores)

def main():
    logger.info("Optuna tuning started (XGBoost)")
    X, y = load_data()
    study = optuna.create_study(direction="maximize")
    study.optimize(lambda t: objective(t, X, y), n_trials=30)
    results = {
        "best_params": study.best_params,
        "best_roc_auc": study.best_value
    }
    with open(TUNING_PATH / "optuna_results.json", "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Best ROC-AUC: {study.best_value:.4f}")
    logger.info(f"Best params: {study.best_params}")
    logger.info("Optuna tuning completed")

if __name__ == "__main__":
    main()
