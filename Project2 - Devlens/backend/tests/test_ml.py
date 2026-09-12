import pytest
from ml.predict import get_issue_predictor

def test_ml_prediction_bug():
    predictor = get_issue_predictor()
    res = predictor.predict(
        title="Application crashes on large file upload",
        body="When uploading a 20MB PDF file, NullPointerException is thrown."
    )
    assert res["predicted_category"] in ["Bug", "Feature", "Question"]
    assert "confidence" in res
    assert 0.0 <= res["confidence"] <= 1.0
    assert len(res["top_predictions"]) >= 2
    assert "important_signals" in res
    assert "model_version" in res

def test_ml_prediction_feature():
    predictor = get_issue_predictor()
    res = predictor.predict(
        title="Please add dark mode theme option to settings dashboard",
        body="Allow switching between light and dark UI mode."
    )
    assert res["predicted_category"] in ["Bug", "Feature", "Question"]
    assert isinstance(res["is_low_confidence"], bool)

def test_ml_prediction_question():
    predictor = get_issue_predictor()
    res = predictor.predict(
        title="How to configure custom DB timeout settings?",
        body="Where in the YAML configuration file can I set max connection timeouts?"
    )
    assert res["predicted_category"] in ["Bug", "Feature", "Question"]
