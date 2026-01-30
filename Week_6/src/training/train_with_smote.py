import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

from xgboost import XGBClassifier

from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE

FEATURE_PATH = Path("src/features")
DATA_PATH = Path("src/data/processed")
EVAL_PATH = Path("src/evaluation")
LOGS_PATH = Path("src/logs")

EVAL_PATH.mkdir(exist_ok=True)
LOGS_PATH.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOGS_PATH / "training_smote.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_data():
    X = pd.read_csv(DATA_PATH/ "X_train.csv")
    y = pd.read_csv(DATA_PATH / "y_train.csv").squeeze()
    with open(FEATURE_PATH / "feature_list.json") as f:
        features = json.load(f)
    X = X[features]
    logger.info(f"Loaded data shape: {X.shape}")
    return X, y

def get_models():
    return {
        "LogisticRegression": LogisticRegression(
            max_iter=1000
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=200,
            random_state=42
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=5,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=42
        ),
        "NeuralNetwork": MLPClassifier(
            hidden_layer_sizes=(64, 32),
            max_iter=500,
            random_state=42
        )
    }

def evaluate_with_smote(X, y, models):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = {
        "accuracy": "accuracy",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
        "roc_auc": "roc_auc"
    }
    results = {}
    for name, model in models.items():
        logger.info(f"Evaluating {name} with SMOTE")
        pipeline = Pipeline([
            ("smote", SMOTE(random_state=42)),
            ("model", model)
        ])
        scores = cross_validate(
            pipeline,
            X,
            y,
            cv=cv,
            scoring=scoring,
            n_jobs=-1
        )
        results[name] = {
            metric: scores[f"test_{metric}"].mean()
            for metric in scoring
        }
        logger.info(
            f"{name} | ROC-AUC: {results[name]['roc_auc']:.4f} "
            f"| Recall: {results[name]['recall']:.4f}"
        )
    return results

def main():
    logger.info("SMOTE training pipeline started")
    X, y = load_data()
    models = get_models()
    results = evaluate_with_smote(X, y, models)
    with open(EVAL_PATH / "metrics_smote.json", "w") as f:
        json.dump(results, f, indent=2)
    logger.info("SMOTE training pipeline completed")

if __name__ == "__main__":
    main()
