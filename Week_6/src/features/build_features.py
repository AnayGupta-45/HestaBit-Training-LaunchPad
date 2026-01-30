import pandas as pd
import numpy as np
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

DATA_PATH = Path("src/data/processed/final.csv")
OUTPUT_PATH = Path("src/data/processed")
LOGS_PATH = Path("src/logs")

OUTPUT_PATH.mkdir(exist_ok=True)
LOGS_PATH.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOGS_PATH / "feature_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_data():
    logger.info("Loading processed data")
    df = pd.read_csv(DATA_PATH)
    logger.info(f"Data loaded with shape {df.shape}")
    return df

def create_features(df):
    logger.info("Creating new features")
    df["is_long_tenure"] = (df["tenure_months"] > 24).astype(int)
    df["is_high_charges"] = (df["monthly_charges"] > df["monthly_charges"].median()).astype(int)
    df["is_high_usage"] = (df["monthly_gb_download"] > df["monthly_gb_download"].median()).astype(int)
    df["support_call_rate"] = df["tech_support_calls"] / (df["tenure_months"] + 1)
    df["late_payment_rate"] = df["late_payments"] / (df["tenure_months"] + 1)
    df["is_recent_login"] = (df["days_since_last_login"] < 30).astype(int)
    df["is_dormant_user"] = (df["days_since_last_login"] > 180).astype(int)
    df["credit_score_bucket"] = pd.cut(
        df["credit_score"],
        bins=[0, 500, 700, 900],
        labels=["low", "medium", "high"]
    )
    df["tenure_bucket"] = pd.cut(
        df["tenure_months"],
        bins=[0, 12, 36, 120],
        labels=["short", "medium", "long"]
    )
    logger.info("Feature creation completed")
    return df

def encode_features(df):
    logger.info("Encoding categorical features")
    categorical_cols = [
        "gender",
        "region",
        "contract_type",
        "internet_service",
        "streaming_package",
        "payment_method",
        "credit_score_bucket",
        "tenure_bucket"
    ]
    df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
    logger.info(f"Encoding completed. Shape: {df.shape}")
    return df

def scale_features(X_train, X_test):
    logger.info("Scaling numerical features")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    return X_train_scaled, X_test_scaled

def split_data(df):
    logger.info("Splitting features and target")
    X = df.drop(columns=["churn_label"])
    y = df["churn_label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )
    logger.info("Train-test split completed")
    return X_train, X_test, y_train, y_test

def save_outputs(X_train, X_test, y_train, y_test):
    logger.info("Saving feature artifacts")
    X_train.to_csv(OUTPUT_PATH / "X_train.csv", index=False)
    X_test.to_csv(OUTPUT_PATH / "X_test.csv", index=False)
    y_train.to_csv(OUTPUT_PATH / "y_train.csv", index=False)
    y_test.to_csv(OUTPUT_PATH / "y_test.csv", index=False)
    logger.info("Feature artifacts saved")

def main():
    logger.info("Feature engineering pipeline started")
    df = load_data()
    df = create_features(df)
    df = encode_features(df)
    X_train, X_test, y_train, y_test = split_data(df)
    X_train_scaled, X_test_scaled = scale_features(X_train, X_test)
    X_train = pd.DataFrame(X_train_scaled, columns=X_train.columns)
    X_test = pd.DataFrame(X_test_scaled, columns=X_test.columns)
    save_outputs(X_train, X_test, y_train, y_test)
    logger.info("Feature engineering pipeline completed")

if __name__ == "__main__":
    main()
