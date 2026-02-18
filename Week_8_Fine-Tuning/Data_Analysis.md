# Dataset Analysis - Week 8 Day 1

## Dataset Used

I used the tatsu-lab/alpaca dataset from HuggingFace.
It had 52,002 samples in instruction/input/output format.

## Problems in the Dataset

- 28 samples had empty outputs
- 674 samples were too short (less than 15 tokens)
- 2,986 samples were too long (more than 256 tokens)
- Total removed: 3,688 samples

## Split the Data into Train and Validation samples

After cleaning I sampled 1,300 rows and split them:

- Train: 1,040 samples
- Validation: 260 samples

## Samples in the Dataset

- QA: 520 samples
- Reasoning: 455 samples
- Extraction: 325 samples

## Token length statistics

- Minimum: 15 tokens
- Maximum: 256 tokens
- Average: 58 tokens
- Median: 45 tokens

## Output files/Deliverables

- data/train.jsonl
- data/val.jsonl
- data/analysis.png
- utils/data_cleaner.py
