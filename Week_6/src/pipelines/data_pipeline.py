import pandas as pd
import logging
from pathlib import Path
import numpy as np

RAW_DATA_PATH = Path("src/data/raw/raw.csv")
PROCESSED_DATA_PATH = Path("src/data/processed/final.csv")
LOGS_PATH = Path("src/logs")

LOGS_PATH.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOGS_PATH / "data_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_data(path: Path) -> pd.DataFrame:
    logger.info(f"Loading raw data from {path}")
    df = pd.read_csv(path)
    logger.info(f"Loaded data with shape {df.shape}")
    return df

def validate_raw_data(df: pd.DataFrame):
    logger.info("Validating raw data")
    if df.empty:
        raise ValueError("Dataset is empty")
    if df.isnull().all().any():
        raise ValueError("One or more columns are fully null")
    logger.info("Raw data validation passed")

def drop_identifiers(df: pd.DataFrame) -> pd.DataFrame:
    if "customer_id" in df.columns:
        df = df.drop(columns=["customer_id"])
        logger.info("Dropped customer_id")
    return df

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Handling missing values")
    df["credit_score_missing"] = df["credit_score"].isnull().astype(int)
    df["credit_score"] = df["credit_score"].fillna(df["credit_score"].median())
    df["tech_support_calls"] = df["tech_support_calls"].fillna(0)
    df["payment_method"] = df["payment_method"].fillna("unknown")
    logger.info("Missing values handled")
    return df

def normalize_categories(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Normalizing categorical columns")
    df["gender"] = (
        df["gender"]
        .str.lower()
        .replace({"m": "male"})
    )
    return df

def handle_outliers_and_transforms(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Applying numeric transformations")
    df["tenure_months"] = df["tenure_months"].clip(upper=120)
    df["monthly_gb_download"] = np.log1p(df["monthly_gb_download"])
    df["account_manager"] = df["account_manager"].astype(bool)
    logger.info("Numeric transformations applied")
    return df

def handle_dates(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Processing date features")
    df["last_login_date"] = pd.to_datetime(
        df["last_login_date"],
        errors="coerce"
    )
    invalid_dates = df["last_login_date"].isnull().sum()
    logger.info(f"Invalid last_login_date entries: {invalid_dates}")
    reference_date = df["last_login_date"].max()
    df["days_since_last_login"] = (
        reference_date - df["last_login_date"]
    ).dt.days
    max_days = df["days_since_last_login"].max()
    df["days_since_last_login"] = df["days_since_last_login"].fillna(max_days + 1)
    df = df.drop(columns=["last_login_date"])
    logger.info("Date features processed successfully")
    return df

def drop_redundant_features(df: pd.DataFrame) -> pd.DataFrame:
    if "total_charges" in df.columns:
        df = df.drop(columns=["total_charges"])
        logger.info("Dropped total_charges due to redundancy")
    return df

def save_processed_data(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info(f"Final dataset saved to {path}")
    logger.info(f"Final shape: {df.shape}")

def main():
    logger.info("Data pipeline started")
    df = load_data(RAW_DATA_PATH)
    validate_raw_data(df)
    df = drop_identifiers(df)
    df = handle_missing_values(df)
    df = normalize_categories(df)
    df = handle_outliers_and_transforms(df)
    df = handle_dates(df)
    df = drop_redundant_features(df)
    save_processed_data(df, PROCESSED_DATA_PATH)
    logger.info("Data pipeline completed successfully")

if __name__ == "__main__":
    main()
