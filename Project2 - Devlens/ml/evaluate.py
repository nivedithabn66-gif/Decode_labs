import time
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report
)

def evaluate_classifier_model(
    model: Any,
    X_train: Any,
    y_train: np.ndarray,
    X_test: Any,
    y_test: np.ndarray,
    label_classes: List[str],
    model_name: str,
    raw_test_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Evaluates a trained classifier on the test set.
    Calculates Accuracy, Precision, Recall, Macro F1, Weighted F1, latency, per-class metrics, confusion matrix, and error analysis samples.
    """
    # Measure Training Time
    start_train = time.time()
    model.fit(X_train, y_train)
    train_time_sec = round(time.time() - start_train, 4)

    # Measure Prediction Time
    start_pred = time.time()
    y_pred = model.predict(X_test)
    pred_time_sec = round(time.time() - start_pred, 4)
    avg_latency_ms = round((pred_time_sec / max(len(y_test), 1)) * 1000, 3)

    # Get Probabilities if available
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_test)
    elif hasattr(model, "decision_function"):
        d = model.decision_function(X_test)
        # Softmax decision function
        exp_d = np.exp(d - np.max(d, axis=1, keepdims=True))
        y_proba = exp_d / np.sum(exp_d, axis=1, keepdims=True)
    else:
        y_proba = None

    acc = float(accuracy_score(y_test, y_pred))
    
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(y_test, y_pred, average="macro", zero_division=0)
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred, labels=range(len(label_classes)))

    # Per-Class Metrics
    per_class_p, per_class_r, per_class_f1, per_class_supp = precision_recall_fscore_support(
        y_test, y_pred, labels=range(len(label_classes)), zero_division=0
    )

    class_metrics = {}
    for idx, class_name in enumerate(label_classes):
        class_metrics[class_name] = {
            "precision": round(float(per_class_p[idx]), 4),
            "recall": round(float(per_class_r[idx]), 4),
            "f1": round(float(per_class_f1[idx]), 4),
            "support": int(per_class_supp[idx])
        }

    # Error Analysis Extraction
    error_samples = []
    correct_samples = []
    low_confidence_samples = []

    for i in range(len(y_test)):
        actual_label = label_classes[y_test[i]]
        pred_label = label_classes[y_pred[i]]
        
        conf = float(np.max(y_proba[i])) if y_proba is not None else 1.0
        
        issue_title = str(raw_test_df.iloc[i].get("title", raw_test_df.iloc[i].get("text", "")[:60]))
        issue_text = str(raw_test_df.iloc[i].get("text", ""))

        sample_obj = {
            "id": i + 1,
            "title": issue_title,
            "text_snippet": issue_text[:200] + "..." if len(issue_text) > 200 else issue_text,
            "actual": actual_label,
            "predicted": pred_label,
            "confidence": round(conf, 4),
            "is_correct": bool(actual_label == pred_label)
        }

        if actual_label != pred_label:
            error_samples.append(sample_obj)
        else:
            correct_samples.append(sample_obj)

        if conf < 0.65:
            low_confidence_samples.append(sample_obj)

    eval_result = {
        "model_name": model_name,
        "accuracy": round(acc, 4),
        "macro_precision": round(float(macro_p), 4),
        "macro_recall": round(float(macro_r), 4),
        "macro_f1": round(float(macro_f1), 4),
        "weighted_precision": round(float(weighted_p), 4),
        "weighted_recall": round(float(weighted_r), 4),
        "weighted_f1": round(float(weighted_f1), 4),
        "train_time_sec": train_time_sec,
        "pred_time_sec": pred_time_sec,
        "avg_latency_ms": avg_latency_ms,
        "confusion_matrix": cm.tolist(),
        "label_classes": label_classes,
        "per_class_metrics": class_metrics,
        "error_samples": error_samples[:20],
        "correct_samples": correct_samples[:10],
        "low_confidence_samples": low_confidence_samples[:10],
        "num_errors": len(error_samples),
        "error_rate": round(len(error_samples) / max(len(y_test), 1), 4)
    }

    return eval_result
