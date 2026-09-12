import pytest
from backend.app.services.quality_service import calculate_issue_quality_score
from backend.app.services.recommendation_service import recommend_priority_and_team
from backend.app.services.duplicate_service import DuplicateDetectionService

def test_quality_score_calculation():
    score_full = calculate_issue_quality_score(
        title="Application crashes when uploading files larger than 10MB",
        description="Detailed description with full context explaining the file upload failure symptom.",
        steps="1. Go to page\n2. Select file\n3. Click submit",
        expected="File uploads cleanly.",
        actual="Page throws 500 error.",
        environment="Windows 11, Python 3.14",
        logs="Traceback: NullPointerException line 42"
    )
    assert score_full["quality_score"] >= 80
    assert score_full["grade"] in ["Excellent", "Good"]

    score_poor = calculate_issue_quality_score(title="Bug", description="Broken")
    assert score_poor["quality_score"] < 50
    assert len(score_poor["missing_elements"]) > 0

def test_recommendations():
    rec = recommend_priority_and_team(
        title="Critical crash in database connection pool",
        description="NullPointerException causes fatal system freeze.",
        category="Bug"
    )
    assert rec["priority_recommendation"]["level"] in ["Critical", "High"]
    assert rec["suggested_team"]["name"] in ["Database", "Backend"]

def test_duplicate_detection():
    dup_engine = DuplicateDetectionService()
    existing = [
        {"id": 1, "title": "Application crashes during file upload", "description": "NullPointerException when uploading files", "category": "Bug"},
        {"id": 2, "title": "Add dark mode toggle", "description": "Support dark theme in header", "category": "Feature"}
    ]
    res = dup_engine.check_duplicates(
        new_title="Application crashes on file upload",
        new_body="NullPointerException throws when uploading large PNG file",
        existing_issues=existing
    )
    assert res["total_matches_found"] > 0
    assert res["max_similarity"] > 0.5
