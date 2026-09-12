import os
import sys
import time
import yaml
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.dataset_loader import detect_and_load_raw_data
from ml.preprocessing import TextPreprocessorTransformer

def run_cross_validation_benchmark(n_splits: int = 5, config_path: str = "ml/config.yaml") -> Dict[str, Any]:
    print(f"[CrossVal] Running Stratified {n_splits}-Fold Cross-Validation Benchmark...")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    train_df, test_df, dataset_info = detect_and_load_raw_data(config["dataset"]["raw_dir"])

    prep_cfg = config.get("preprocessing", {})
    vec_cfg = config.get("vectorizer", {})

    le = LabelEncoder()
    y_train = le.fit_transform(train_df["label"].tolist())
    y_test = le.transform(test_df["label"].tolist()) if test_df is not None else None

    X_train_raw = train_df["text"].tolist()
    X_test_raw = test_df["text"].tolist() if test_df is not None else []

    candidate_classifiers = {
        "Linear SVM": CalibratedClassifierCV(LinearSVC(C=1.0, random_state=42, dual="auto"), cv=3),
        "Logistic Regression": LogisticRegression(C=1.0, max_iter=1000, random_state=42),
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.5),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42)
    }

    cv_results = []
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    for m_name, clf in candidate_classifiers.items():
        pipeline = Pipeline([
            ('preprocessor', TextPreprocessorTransformer(
                lowercase=prep_cfg.get("lowercase", True),
                remove_whitespace=prep_cfg.get("remove_whitespace", True),
                remove_punctuation=prep_cfg.get("remove_punctuation", False),
                remove_stopwords=prep_cfg.get("remove_stopwords", True)
            )),
            ('tfidf', TfidfVectorizer(
                ngram_range=tuple(vec_cfg.get("ngram_range", [1, 2])),
                max_features=vec_cfg.get("max_features", 10000),
                min_df=vec_cfg.get("min_df", 2),
                max_df=vec_cfg.get("max_df", 0.95)
            )),
            ('clf', clf)
        ])

        # Run CV scoring
        scoring = ['accuracy', 'f1_macro', 'f1_weighted', 'precision_macro', 'recall_macro']
        t0 = time.time()
        scores = cross_validate(pipeline, X_train_raw, y_train, cv=skf, scoring=scoring, n_jobs=1)
        fit_time_total = time.time() - t0

        # Fit on full train set to measure test accuracy and latency
        pipeline.fit(X_train_raw, y_train)
        
        t_pred_0 = time.time()
        test_preds = pipeline.predict(X_test_raw) if X_test_raw else []
        pred_latency_ms = ((time.time() - t_pred_0) / max(len(X_test_raw), 1)) * 1000.0

        from sklearn.metrics import accuracy_score, f1_score
        test_acc = accuracy_score(y_test, test_preds) if len(X_test_raw) > 0 else 0.0
        test_macro_f1 = f1_score(y_test, test_preds, average="macro") if len(X_test_raw) > 0 else 0.0

        cv_results.append({
            "model_name": m_name,
            "cv_macro_f1_mean": float(np.mean(scores['test_f1_macro'])),
            "cv_macro_f1_std": float(np.std(scores['test_f1_macro'])),
            "cv_accuracy_mean": float(np.mean(scores['test_accuracy'])),
            "test_macro_f1": float(test_macro_f1),
            "test_accuracy": float(test_acc),
            "train_time_sec": float(fit_time_total / n_splits),
            "pred_latency_ms": float(pred_latency_ms)
        })

    best_cv_model = max(cv_results, key=lambda x: x["cv_macro_f1_mean"])
    print("\n" + "="*85)
    print(f"{'MODEL':<25} | {'CV MACRO F1':<15} | {'TEST MACRO F1':<15} | {'TEST ACC':<10} | {'LATENCY':<8}")
    print("="*85)
    for r in cv_results:
        f1_str = f"{r['cv_macro_f1_mean']:.4f} (±{r['cv_macro_f1_std']:.4f})"
        print(f"{r['model_name']:<25} | {f1_str:<15} | {r['test_macro_f1']:<15.4f} | {r['test_accuracy']:<10.4f} | {r['pred_latency_ms']:<6.2f}ms")
    print("="*85 + "\n")

    print(f"[CrossVal] Best Model Selected by CV Macro F1: {best_cv_model['model_name']} ({best_cv_model['cv_macro_f1_mean']:.4f})")

    report = {
        "n_splits": n_splits,
        "best_model": best_cv_model["model_name"],
        "benchmark": cv_results
    }
    
    os.makedirs("models", exist_ok=True)
    with open("models/cross_validation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report

if __name__ == "__main__":
    run_cross_validation_benchmark()
