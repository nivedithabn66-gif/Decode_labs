# DevLens Dataset Directory Structure

- `raw/`: Place the Kaggle GitHub Bugs Prediction dataset files (`Train.json`, `Test.json`, `train.csv`, `test.csv`, or `Train_extra.json`) here.
- `processed/`: Formatted, cleaned, and split datasets processed by the DevLens NLP pipeline.

## Setup Instructions

1. Download the dataset from Kaggle: [GitHub Bugs Prediction Dataset](https://www.kaggle.com/datasets/anmolkumar/github-bugs-prediction)
2. Extract the files (`Train.json` and `Test.json` or `.csv` files) into `data/raw/`.
3. DevLens automatically detects format, inspects columns (`Title`, `Body`, `Label`), handles missing values, and maps labels (0: Bug, 1: Feature, 2: Question).
4. Run dataset exploration & feature pipeline:
   ```bash
   python ml/train.py
   ```
