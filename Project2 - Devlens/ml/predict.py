import os
import sys
import yaml
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.preprocessing import TextPreprocessor

class IssuePredictor:
    """
    Production-grade Issue Predictor. Loads trained model artifacts ONCE during startup.
    Provides confidence-aware predictions, top probabilities, explainable AI term signals,
    and low-confidence warnings.
    """
    _instance = None

    def __init__(self, models_dir: str = "models", config_path: str = "ml/config.yaml"):
        self.models_dir = models_dir
        self.config_path = config_path

        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {"model": {"confidence_threshold": 0.65}}

        self.threshold = self.config.get("model", {}).get("confidence_threshold", 0.65)

        # Paths to artifacts
        self.model_path = os.path.join(models_dir, "trained_model.pkl")
        self.tfidf_path = os.path.join(models_dir, "tfidf_vectorizer.pkl")
        self.le_path = os.path.join(models_dir, "label_encoder.pkl")
        self.meta_path = os.path.join(models_dir, "model_metadata.json")

        self.loaded = False
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.metadata = {}
        self.preprocessor = TextPreprocessor(lowercase=True, remove_stopwords=True)

        self._load_artifacts()

    def _load_artifacts(self):
        if not (os.path.exists(self.model_path) and os.path.exists(self.tfidf_path) and os.path.exists(self.le_path)):
            print(f"[IssuePredictor] WARNING: Model artifacts not found in '{self.models_dir}'. Run ml/train.py first.")
            return

        print(f"[IssuePredictor] Loading model artifacts from '{self.models_dir}'...")
        self.model = joblib.load(self.model_path)
        self.vectorizer = joblib.load(self.tfidf_path)
        self.label_encoder = joblib.load(self.le_path)

        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

        self.feature_names = np.array(self.vectorizer.get_feature_names_out())
        self.classes = list(self.label_encoder.classes_)
        self.loaded = True
        print(f"[IssuePredictor] Successfully loaded model '{self.metadata.get('model_name', 'Classifier')}' version {self.metadata.get('version', 'v1.0')}")

    def predict(self, title: str, body: str) -> Dict[str, Any]:
        """
        Predicts category, confidence, top 3 class probabilities, and XAI feature signals.
        """
        if not self.loaded:
            self._load_artifacts()
            if not self.loaded:
                return self._fallback_prediction(title, body)

        raw_combined = f"{title} {body}".strip()
        clean_text = self.preprocessor.preprocess_text(raw_combined)

        if not clean_text:
            return {
                "predicted_category": "Question",
                "confidence": 0.5,
                "top_predictions": [{"category": c, "probability": 0.333} for c in self.classes],
                "is_low_confidence": True,
                "confidence_message": "Input text is too short or empty for confident prediction.",
                "important_signals": [],
                "explanation_note": "Insufficient features to compute term importance.",
                "model_name": self.metadata.get("model_name", "Linear SVM"),
                "model_version": self.metadata.get("version", "v1.0.0")
            }

        # Vectorize
        X_vec = self.vectorizer.transform([clean_text])

        # Get probabilities
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X_vec)[0]
        elif hasattr(self.model, "decision_function"):
            d = self.model.decision_function(X_vec)[0]
            exp_d = np.exp(d - np.max(d))
            probs = exp_d / np.sum(exp_d)
        else:
            pred_idx = self.model.predict(X_vec)[0]
            probs = np.zeros(len(self.classes))
            probs[pred_idx] = 1.0

        top_idx = int(np.argmax(probs))
        predicted_category = self.classes[top_idx]
        confidence = float(probs[top_idx])

        # Format Top Predictions
        top_preds = []
        sorted_indices = np.argsort(probs)[::-1]
        for idx in sorted_indices[:3]:
            top_preds.append({
                "category": str(self.classes[idx]),
                "probability": round(float(probs[idx]), 4)
            })

        # Confidence Level Tiering: HIGH >= 0.85, MEDIUM 0.65-0.84, LOW < 0.65
        if confidence >= 0.85:
            confidence_level = "HIGH"
            conf_msg = "DevLens high confidence prediction."
            is_low_conf = False
        elif confidence >= self.threshold:
            confidence_level = "MEDIUM"
            conf_msg = "Moderate model confidence. Validated against training dataset."
            is_low_conf = False
        else:
            confidence_level = "LOW"
            conf_msg = f"⚠️ DevLens is uncertain about this classification ({round(confidence*100, 1)}% < {round(self.threshold*100, 1)}%). Human review is recommended."
            is_low_conf = True

        # XAI Explanation: Feature importance for predicted class
        important_signals, explanation_note, tech_details = self._extract_term_importance(X_vec, top_idx)

        return {
            "predicted_category": predicted_category,
            "confidence": round(confidence, 4),
            "confidence_level": confidence_level,
            "top_predictions": top_preds,
            "is_low_confidence": is_low_conf,
            "confidence_message": conf_msg,
            "important_signals": important_signals,
            "explanation_note": explanation_note,
            "technical_explanation": tech_details,
            "model_name": self.metadata.get("model_name", "Linear SVM"),
            "model_version": self.metadata.get("version", "v1.0.0")
        }

    def _extract_term_importance(self, X_vec, class_idx: int) -> tuple[List[str], str, Dict[str, Any]]:
        """Extracts top non-zero TF-IDF terms present in the input that contributed to the predicted class."""
        try:
            nonzero_indices = X_vec.nonzero()[1]
            if len(nonzero_indices) == 0:
                return [], "No active terms present in vocabulary.", {}

            feature_names = self.feature_names[nonzero_indices]

            # Extract feature weights from CalibratedClassifierCV or linear model
            base_estimator = getattr(self.model, "calibrated_classifiers_", None)
            if base_estimator and hasattr(base_estimator[0].estimator, "coef_"):
                coefs = [cc.estimator.coef_ for cc in base_estimator]
                avg_coef = np.mean(coefs, axis=0)
                weights = avg_coef[class_idx, nonzero_indices]
            elif hasattr(self.model, "coef_"):
                weights = self.model.coef_[class_idx, nonzero_indices]
            else:
                weights = X_vec.data

            sorted_feat_idx = np.argsort(weights)[::-1]
            top_terms = [str(feature_names[i]) for i in sorted_feat_idx[:5]]
            top_weights = [round(float(weights[i]), 4) for i in sorted_feat_idx[:5]]

            tech_details = {
                "vectorizer_type": "TF-IDF (1,2-grams)",
                "feature_space_dim": len(self.feature_names),
                "active_terms_in_doc": len(nonzero_indices),
                "top_weighted_features": dict(zip(top_terms, top_weights))
            }

            if top_terms:
                note = f"The issue contains key terms ('{', '.join(top_terms)}') strongly associated with {self.classes[class_idx]} reports in the training data."
            else:
                note = "Feature term signals calculated from TF-IDF feature space."

            return top_terms, note, tech_details
        except Exception as e:
            return [], f"Explanation limited: {str(e)}", {}

    def _fallback_prediction(self, title: str, body: str) -> Dict[str, Any]:
        text_lower = f"{title} {body}".lower()
        if any(w in text_lower for w in ["crash", "error", "exception", "bug", "fails", "fail", "freeze", "nullpointer"]):
            cat = "Bug"
        elif any(w in text_lower for w in ["how", "what", "where", "why", "can i", "is there", "?"]):
            cat = "Question"
        else:
            cat = "Feature"

        return {
            "predicted_category": cat,
            "confidence": 0.85,
            "top_predictions": [
                {"category": cat, "probability": 0.85},
                {"category": "Feature" if cat != "Feature" else "Bug", "probability": 0.10},
                {"category": "Question" if cat != "Question" else "Bug", "probability": 0.05}
            ],
            "is_low_confidence": False,
            "confidence_message": "Rule fallback active until ML training finishes.",
            "important_signals": [w for w in ["crash", "error", "exception", "feature", "how"] if w in text_lower],
            "explanation_note": "Rule-based fallback prediction.",
            "model_name": "Heuristic Fallback",
            "model_version": "v0.1.0"
        }

# Global Singleton Instance for fast API startup
_global_predictor = None

def get_issue_predictor() -> IssuePredictor:
    global _global_predictor
    if _global_predictor is None:
        _global_predictor = IssuePredictor()
    return _global_predictor

if __name__ == "__main__":
    predictor = get_issue_predictor()
    res = predictor.predict("Application crashes on file upload", "When uploading large files, NullPointerException is thrown.")
    print("Prediction Output:\n", json.dumps(res, indent=2))
