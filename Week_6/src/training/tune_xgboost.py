import json
import logging
from pathlib import Path

import joblib
import optuna
import pandas as pd
import xgboost as xgb

from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

DATA_PATH = Path("src/data/processed")
FEATURE_PATH = Path("src/features")
MODEL_PATH = Path("src/models")
LOGS_PATH = Path("src/logs")
TUNING_PATH = Path("src/tuning")

MODEL_PATH.mkdir(exist_ok=True)
LOGS_PATH.mkdir(exist_ok=True)
TUNING_PATH.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOGS_PATH / "xgboost_tuning.log"),
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

def objective(trial, X, y, scale_pos_weight):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 400),
        "max_depth": trial.suggest_int("max_depth", 2, 6),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        "gamma": trial.suggest_float("gamma", 0.0, 5.0),
        "scale_pos_weight": scale_pos_weight,
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "random_state": 42,
        "n_jobs": -1
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    aucs = []
    for train_idx, val_idx in cv.split(X, y):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train)
        preds = model.predict_proba(X_val)[:, 1]
        aucs.append(roc_auc_score(y_val, preds))
    return sum(aucs) / len(aucs)

def main():
    logger.info("XGBoost Optuna tuning started")
    X, y = load_data()
    pos = (y == 1).sum()
    neg = (y == 0).sum()
    scale_pos_weight = neg / pos
    logger.info(f"scale_pos_weight set to {scale_pos_weight:.2f}")
    study = optuna.create_study(direction="maximize")
    study.optimize(lambda t: objective(t, X, y, scale_pos_weight), n_trials=40)
    best_params = study.best_params
    best_params.update({
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "random_state": 42,
        "n_jobs": -1
    })
    logger.info(f"Best ROC-AUC: {study.best_value:.4f}")
    logger.info(f"Best params: {best_params}")
    final_model = xgb.XGBClassifier(**best_params)
    final_model.fit(X, y)
    joblib.dump(final_model, MODEL_PATH / "xgboost_best.pkl")
    with open(TUNING_PATH / "xgboost_results.json", "w") as f:
        json.dump({
            "best_roc_auc": study.best_value,
            "best_params": best_params
        }, f, indent=2)
    logger.info("XGBoost tuning completed and model saved")

if __name__ == "__main__":
    main()
