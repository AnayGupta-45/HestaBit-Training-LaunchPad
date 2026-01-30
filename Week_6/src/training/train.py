import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

from xgboost import XGBClassifier

DATA_PATH = Path("src/data/processed")
MODEL_PATH = Path("src/models")
EVAL_PATH = Path("src/evaluation")
LOGS_PATH = Path("src/logs")
FEATURE_PATH = Path("src/features")

MODEL_PATH.mkdir(exist_ok=True)
EVAL_PATH.mkdir(exist_ok=True)
LOGS_PATH.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOGS_PATH / "training.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def load_data():
    X_train = pd.read_csv(DATA_PATH / "X_train.csv")
    X_test = pd.read_csv(DATA_PATH / "X_test.csv")
    y_train = pd.read_csv(DATA_PATH / "y_train.csv").squeeze()
    y_test = pd.read_csv(DATA_PATH / "y_test.csv").squeeze()

    with open(FEATURE_PATH / "feature_list.json") as f:
        selected_features = json.load(f)
    X_train = X_train[selected_features]
    X_test = X_test[selected_features]
    logger.info(f"Training data shape: {X_train.shape}")
    logger.info(f"Testing data shape: {X_test.shape}")
    return X_train, X_test, y_train, y_test

def get_models():
    return {
        "LogisticRegression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced"
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

def evaluate_models(X, y, models):
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
        logger.info(f"Evaluating {name}")
        scores = cross_validate(
            model,
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
        logger.info(f"{name} ROC-AUC: {results[name]['roc_auc']:.4f}")
    return results

def select_best_model(results):
    best_model = max(results, key=lambda m: results[m]["roc_auc"])
    logger.info(f"Best model selected: {best_model}")
    return best_model

def train_and_save_best_model(
    model, X_train, y_train, X_test, y_test
):
    model.fit(X_train, y_train)
    joblib.dump(model, MODEL_PATH / "best_model.pkl")
    logger.info("Best model saved")
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(cm)
    disp.plot()
    plt.tight_layout()
    plt.savefig(EVAL_PATH / "confusion_matrix.png")
    plt.close()
    logger.info("Confusion matrix saved")

def main():
    logger.info("Training pipeline started")

    X_train, X_test, y_train, y_test = load_data()
    models = get_models()

    results = evaluate_models(X_train, y_train, models)

    with open(EVAL_PATH / "metrics.json", "w") as f:
        json.dump(results, f, indent=2)

    best_model_name = select_best_model(results)
    best_model = models[best_model_name]

    train_and_save_best_model(
        best_model, X_train, y_train, X_test, y_test
    )
    logger.info("Training pipeline completed successfully")


if __name__ == "__main__":
    main()
