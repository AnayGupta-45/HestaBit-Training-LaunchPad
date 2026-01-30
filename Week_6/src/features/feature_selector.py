import pandas as pd
import logging
from pathlib import Path
import json
import matplotlib.pyplot as plt

from sklearn.feature_selection import mutual_info_classif, RFE
from sklearn.linear_model import LogisticRegression

FEATURE_PATH = Path("src/features")
DATA_PATH = Path("src/data/processed")
LOGS_PATH = Path("src/logs")
EVAL_PATH = Path("src/evaluation")

FEATURE_PATH.mkdir(exist_ok=True)
LOGS_PATH.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOGS_PATH / "feature_selector.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def load_data():
    X = pd.read_csv(DATA_PATH / "X_train.csv")
    y = pd.read_csv(DATA_PATH / "y_train.csv").squeeze()
    logger.info(f"Loaded X: {X.shape}, y: {y.shape}")
    return X, y


def correlation_scores(X, y):
    corr = X.join(y).corr()["churn_label"].abs().drop("churn_label")
    return corr


def mutual_info_scores(X, y):
    mi = mutual_info_classif(X, y, random_state=42)
    return pd.Series(mi, index=X.columns)


def rfe_scores(X, y):
    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    rfe = RFE(model, n_features_to_select=len(X.columns) // 2)
    rfe.fit(X, y)
    return pd.Series(rfe.ranking_, index=X.columns)


def build_final_importance(corr, mi, rfe):
    df = pd.DataFrame({
        "correlation": corr.rank(ascending=False),
        "mutual_info": mi.rank(ascending=False),
        "rfe": rfe.rank(ascending=True)
    })

    df["final_rank"] = df.mean(axis=1)
    df = df.sort_values("final_rank")

    return df


def plot_feature_importance(df, top_n=15):
    plt.figure(figsize=(10, 4))
    df.head(top_n)["final_rank"].plot(kind="bar")
    plt.title("Final Feature Importance (Correlation + MI + RFE)")
    plt.ylabel("Average Rank (Lower = Better)")
    plt.tight_layout()
    plt.savefig(EVAL_PATH / "feature_importance.png")
    plt.close()

    logger.info("Final feature importance plot saved")

def main():
    logger.info("Feature selection started")

    X, y = load_data()
    corr = correlation_scores(X, y)
    mi = mutual_info_scores(X, y)
    rfe = rfe_scores(X, y)
    final_importance = build_final_importance(corr, mi, rfe)
    selected_features = final_importance.head(20).index.tolist()
    with open(FEATURE_PATH / "feature_list.json", "w") as f:
        json.dump(selected_features, f, indent=2)
    plot_feature_importance(final_importance)
    logger.info("Top selected features:")
    for f in selected_features:
        logger.info(f)
    logger.info("Feature selection completed")


if __name__ == "__main__":
    main()
