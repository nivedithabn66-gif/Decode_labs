import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import pandas as pd
import numpy as np
from typing import Dict, Any
from ml.dataset_loader import detect_and_load_raw_data

def run_exploratory_data_analysis(output_json: str = "data/processed/eda_summary.json") -> Dict[str, Any]:
    print("[EDA] Starting Exploratory Data Analysis workflow...")
    train_df, test_df, dataset_info = detect_and_load_raw_data()
    
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    
    # Calculate word and char length metrics
    train_df["char_length"] = train_df["text"].str.len()
    train_df["word_count"] = train_df["text"].apply(lambda x: len(str(x).split()))
    
    class_dist = train_df["label"].value_counts().to_dict()
    class_percentages = (train_df["label"].value_counts(normalize=True) * 100).round(2).to_dict()
    
    avg_words_per_class = train_df.groupby("label")["word_count"].mean().round(2).to_dict()
    avg_chars_per_class = train_df.groupby("label")["char_length"].mean().round(2).to_dict()
    
    length_quantiles = {
        "word_count_p25": float(train_df["word_count"].quantile(0.25)),
        "word_count_median": float(train_df["word_count"].median()),
        "word_count_p75": float(train_df["word_count"].quantile(0.75)),
        "char_len_median": float(train_df["char_length"].median()),
    }
    
    imbalance_ratio = round(max(class_dist.values()) / min(class_dist.values()), 2)
    
    eda_summary = {
        "dataset_source": dataset_info.get("status", "unknown"),
        "raw_train_file": dataset_info.get("train_file", "None"),
        "raw_test_file": dataset_info.get("test_file", "None"),
        "num_train_examples": len(train_df),
        "num_test_examples": len(test_df) if test_df is not None else 0,
        "total_examples": len(train_df) + (len(test_df) if test_df is not None else 0),
        "columns": list(train_df.columns),
        "data_types": {col: str(train_df[col].dtype) for col in train_df.columns},
        "missing_values": {
            "title_missing": int(train_df["title"].str.strip().eq("").sum()) if "title" in train_df else 0,
            "body_missing": int(train_df["body"].str.strip().eq("").sum()) if "body" in train_df else 0,
            "text_missing": int(train_df["text"].str.strip().eq("").sum()),
            "label_missing": int(train_df["label"].isna().sum())
        },
        "duplicate_records": int(train_df.duplicated(subset=["text"]).sum()),
        "class_distribution": class_dist,
        "class_percentages": class_percentages,
        "class_imbalance_ratio": imbalance_ratio,
        "text_length_distribution": {
            "avg_word_count_by_class": avg_words_per_class,
            "avg_char_count_by_class": avg_chars_per_class,
            "overall_avg_words": round(float(train_df["word_count"].mean()), 2),
            "overall_avg_chars": round(float(train_df["char_length"].mean()), 2),
            "quantiles": length_quantiles
        }
    }
    
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(eda_summary, f, indent=2)
        
    print(f"[EDA] Summary saved to {output_json}")
    return eda_summary

if __name__ == "__main__":
    summary = run_exploratory_data_analysis()
    print("EDA Complete:", json.dumps(summary, indent=2))
