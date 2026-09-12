import os
import sys

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import yaml
import json
import joblib
import datetime
import numpy as np
import pandas as pd
from typing import Dict, Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import LinearSVC

from ml.dataset_loader import detect_and_load_raw_data
from ml.preprocessing import TextPreprocessor
from ml.evaluate import evaluate_classifier_model
from ml.eda import run_exploratory_data_analysis

def train_and_evaluate_models(config_path: str = "ml/config.yaml") -> Dict[str, Any]:
    print("[Train] Loading configuration from:", config_path)
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 1. Run EDA and retrieve dataset
    eda_summary = run_exploratory_data_analysis()
    train_df, test_df, dataset_info = detect_and_load_raw_data(config["dataset"]["raw_dir"])

    # 2. NLP Preprocessing
    prep_cfg = config.get("preprocessing", {})
    preprocessor = TextPreprocessor(
        lowercase=prep_cfg.get("lowercase", True),
        remove_whitespace=prep_cfg.get("remove_whitespace", True),
        remove_punctuation=prep_cfg.get("remove_punctuation", False),
        remove_stopwords=prep_cfg.get("remove_stopwords", True)
    )

    print("[Train] Preprocessing text data...")
    train_text_clean = preprocessor.preprocess_series(train_df["text"].tolist())
    test_text_clean = preprocessor.preprocess_series(test_df["text"].tolist())

    # 3. Label Encoding
    le = LabelEncoder()
    y_train = le.fit_transform(train_df["label"].tolist())
    y_test = le.transform(test_df["label"].tolist())
    label_classes = list(le.classes_)

    # 4. Feature Extraction - TF-IDF Vectorizer
    vec_cfg = config.get("vectorizer", {})
    tfidf = TfidfVectorizer(
        ngram_range=tuple(vec_cfg.get("ngram_range", [1, 2])),
        max_features=vec_cfg.get("max_features", 10000),
        min_df=vec_cfg.get("min_df", 2),
        max_df=vec_cfg.get("max_df", 0.95)
    )

    print("[Train] Fitting TF-IDF Vectorizer on training split only...")
    X_train = tfidf.fit_transform(train_text_clean)
    X_test = tfidf.transform(test_text_clean)

    print(f"[Train] Feature matrix shape: Train {X_train.shape}, Test {X_test.shape}")

    # 5. Define Candidate Models
    candidate_models = {
        "Linear SVM": CalibratedClassifierCV(LinearSVC(C=1.0, random_state=42, dual="auto"), cv=3),
        "Logistic Regression": LogisticRegression(C=1.0, max_iter=1000, random_state=42),
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.5),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42)
    }

    comparison_results = []
    trained_model_objs = {}
    evaluation_details = {}

    print("\n" + "="*70)
    print(f"{'MODEL':<25} | {'ACCURACY':<10} | {'MACRO F1':<10} | {'WEIGHTED F1':<11} | {'LATENCY':<8}")
    print("="*70)

    for m_name, model_inst in candidate_models.items():
        eval_res = evaluate_classifier_model(
            model=model_inst,
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            label_classes=label_classes,
            model_name=m_name,
            raw_test_df=test_df
        )

        trained_model_objs[m_name] = model_inst
        evaluation_details[m_name] = eval_res

        comparison_results.append({
            "model_name": m_name,
            "accuracy": eval_res["accuracy"],
            "macro_precision": eval_res["macro_precision"],
            "macro_recall": eval_res["macro_recall"],
            "macro_f1": eval_res["macro_f1"],
            "weighted_f1": eval_res["weighted_f1"],
            "train_time_sec": eval_res["train_time_sec"],
            "pred_latency_ms": eval_res["avg_latency_ms"]
        })

        print(f"{m_name:<25} | {eval_res['accuracy']:<10.4f} | {eval_res['macro_f1']:<10.4f} | {eval_res['weighted_f1']:<11.4f} | {eval_res['avg_latency_ms']:<6.2f}ms")

    print("="*70 + "\n")

    # 6. Auto-select best model using MACRO F1
    best_model_info = max(comparison_results, key=lambda x: x["macro_f1"])
    best_model_name = best_model_info["model_name"]
    best_model_obj = trained_model_objs[best_model_name]
    best_eval = evaluation_details[best_model_name]

    print(f"[Train] BEST MODEL SELECTED: '{best_model_name}' (Macro F1: {best_model_info['macro_f1']})")

    # 7. Save Model Artifacts
    output_dir = config["model"]["output_dir"]
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(config["dataset"]["processed_dir"]), exist_ok=True)

    joblib.dump(best_model_obj, os.path.join(output_dir, "trained_model.pkl"))
    joblib.dump(tfidf, os.path.join(output_dir, "tfidf_vectorizer.pkl"))
    joblib.dump(le, os.path.join(output_dir, "label_encoder.pkl"))

    # Save Preprocessor Config & Version Metadata
    version = config["model"]["version"]
    timestamp = datetime.datetime.now().isoformat()

    metadata = {
        "model_name": best_model_name,
        "version": f"v{version}",
        "training_timestamp": timestamp,
        "primary_metric": "macro_f1",
        "best_macro_f1": best_eval["macro_f1"],
        "best_accuracy": best_eval["accuracy"],
        "dataset_source": dataset_info.get("status", "benchmark"),
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "num_features": X_train.shape[1],
        "label_classes": label_classes,
        "vectorizer_config": vec_cfg,
        "preprocessing_config": preprocessor.to_dict(),
        "candidate_comparisons": comparison_results
    }

    with open(os.path.join(output_dir, "model_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    with open(os.path.join(output_dir, "classification_report.json"), "w", encoding="utf-8") as f:
        json.dump(best_eval["per_class_metrics"], f, indent=2)

    with open(os.path.join(output_dir, "confusion_matrix.json"), "w", encoding="utf-8") as f:
        json.dump({
            "labels": label_classes,
            "matrix": best_eval["confusion_matrix"]
        }, f, indent=2)

    with open(os.path.join(output_dir, "error_samples.json"), "w", encoding="utf-8") as f:
        json.dump(best_eval["error_samples"], f, indent=2)

    print(f"[Train] Model artifacts successfully saved to '{output_dir}/'.")
    return metadata

if __name__ == "__main__":
    meta = train_and_evaluate_models()
    print("Training pipeline finished cleanly.")
