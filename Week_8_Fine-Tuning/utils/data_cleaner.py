import os
import json
import logging
import pandas as pd
from datasets import load_dataset
import matplotlib.pyplot as plt


SEED = 42
MIN_TOKENS = 15
MAX_TOKENS = 256
DATA_DIR = "data"
OUTPUTS_DIR = "output"
SAMPLE_SIZE = {"qa": 520, "reasoning": 455, "extraction": 325}


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    handlers=[logging.FileHandler("logs/data_cleaner.log"), logging.StreamHandler()],
)
log = logging.getLogger(__name__)


# load dataset and keep only required columns
def load_data():
    df = pd.DataFrame(load_dataset("tatsu-lab/alpaca")["train"])
    df = df[["instruction", "input", "output"]].copy()
    log.info(f"loaded {len(df)} rows")
    return df


# calculate token length for each sample
def add_token_length(df):
    df["token_length"] = df.apply(
        lambda row: len(f"{row['instruction']} {row['input']} {row['output']}".split()),
        axis=1,
    )
    return df


# remove empty, too short, and too long samples
def clean(df):
    before = len(df)
    df = df[
        (df["output"] != "")
        & (df["token_length"] >= MIN_TOKENS)
        & (df["token_length"] <= MAX_TOKENS)
    ].reset_index(drop=True)
    log.info(f"removed {before - len(df)} samples | remaining: {len(df)}")
    return df


# assign a type label based on instruction keywords
def label_type(instruction):
    text = instruction.lower()
    if any(k in text for k in ["extract", "list", "identify", "find", "summarize"]):
        return "extraction"
    if any(k in text for k in ["why", "should", "compare", "analyze", "explain"]):
        return "reasoning"
    if any(k in text for k in ["what", "who", "when", "where", "how"]):
        return "qa"
    return "other"


# sample fixed number of rows from each category
def sample_data(df):
    df["type"] = df["instruction"].apply(label_type)
    qa = df[df["type"] == "qa"].sample(SAMPLE_SIZE["qa"], random_state=SEED)
    reasoning = df[df["type"] == "reasoning"].sample(
        SAMPLE_SIZE["reasoning"], random_state=SEED
    )
    extraction = df[df["type"] == "extraction"].sample(
        SAMPLE_SIZE["extraction"], random_state=SEED
    )
    result = (
        pd.concat([qa, reasoning, extraction])
        .sample(frac=1, random_state=SEED)
        .reset_index(drop=True)
    )
    log.info(f"sampled {len(result)} rows | breakdown: {SAMPLE_SIZE}")
    return result


# write dataframe rows to a jsonl file
def save_jsonl(df, path):
    with open(path, "w") as f:
        for _, row in df.iterrows():
            f.write(
                json.dumps(
                    {
                        "instruction": row["instruction"],
                        "input": row["input"],
                        "output": row["output"],
                    }
                )
                + "\n"
            )
    log.info(f"saved {len(df)} rows → {path}")

# plot and save token length and category distribution
def plot_analysis(df):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    df["token_length"].hist(bins=40, ax=axes[0], color="steelblue", edgecolor="black")
    axes[0].set_title("Token Length Distribution")

    df["type"].value_counts().plot(kind="bar", ax=axes[1], color="steelblue", edgecolor="black")
    axes[1].set_title("Category Distribution")
    axes[1].tick_params(axis="x", rotation=0)

    plt.tight_layout()
    plt.savefig(f"{OUTPUTS_DIR}/analysis.png")
    log.info(f"graph saved → {OUTPUTS_DIR}/analysis.png")


# run the full pipeline
def main():
    df = load_data()
    df = add_token_length(df)
    df = clean(df)
    df = sample_data(df)

    split = int(len(df) * 0.8)
    train_df = df[:split]
    val_df = df[split:]

    os.makedirs(DATA_DIR, exist_ok=True)
    save_jsonl(train_df, f"{DATA_DIR}/train.jsonl")
    save_jsonl(val_df, f"{DATA_DIR}/val.jsonl")
    plot_analysis(df)
    
if __name__ == "__main__":
    main()
