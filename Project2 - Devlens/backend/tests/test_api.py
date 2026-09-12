import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.init_db import init_database

# Initialize test database
init_database()

client = TestClient(app)

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["service"] == "DevLens AI Platform API"
    assert data["status"] == "online"

def test_analyze_issue_endpoint():
    payload = {
        "title": "Application crashes during large file upload",
        "description": "When uploading a 20MB file, system throws NullPointerException at line 42.",
        "steps_to_reproduce": "1. Upload file",
        "expected_behavior": "Upload succeeds",
        "actual_behavior": "Throws 500",
        "environment": "Windows 11",
        "logs": "NullPointerException"
    }
    res = client.post("/api/issues/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "predicted_category" in data
    assert "confidence" in data
    assert "quality_score" in data
    assert "priority_recommendation" in data
    assert "suggested_team" in data
    assert "duplicate_check" in data

def test_create_and_list_issues():
    payload = {
        "title": "Add dark mode toggle for dashboard view",
        "description": "Please support dark mode theme across all dashboard views.",
        "confirmed_category": "Feature"
    }
    create_res = client.post("/api/issues", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["title"] == payload["title"]

    list_res = client.get("/api/issues")
    assert list_res.status_code == 200
    issues_list = list_res.json()
    assert len(issues_list) > 0

def test_dashboard_stats():
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_issues" in data
    assert "bugs" in data
    assert "features" in data
    assert "questions" in data
    assert "macro_f1" in data

def test_model_info_and_metrics():
    info_res = client.get("/api/model/info")
    assert info_res.status_code == 200
    info_data = info_res.json()
    assert "model_name" in info_data
    assert "version" in info_data

    metrics_res = client.get("/api/model/metrics")
    assert metrics_res.status_code == 200

def test_system_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["api_status"] == "Operational"

def test_compare_issues_endpoint():
    payload = {
        "title_a": "Application crashes during file upload",
        "description_a": "NullPointerException at line 42",
        "title_b": "Server fails on big file upload",
        "description_b": "Upload freezes with 500 error"
    }
    res = client.post("/api/issues/compare", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "similarity_percentage" in data
    assert "common_terms" in data
    assert "comparison_summary" in data

def test_model_health_and_registry():
    health_res = client.get("/api/model/health")
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert "model_status" in health_data

    registry_res = client.get("/api/model/registry")
    assert registry_res.status_code == 200
    registry_data = registry_res.json()
    assert "registry" in registry_data
    assert len(registry_data["registry"]) > 0

def test_distribution_shift():
    res = client.get("/api/model/distribution-shift")
    assert res.status_code == 200
    data = res.json()
    assert "training_distribution" in data
    assert "production_distribution" in data

