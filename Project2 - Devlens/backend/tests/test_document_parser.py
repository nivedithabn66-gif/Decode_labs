import pytest
from backend.app.services.document_parser import parse_uploaded_file, generate_error_rectification

def test_raw_text_file_parsing():
    content = b"Application crash with NullPointerException\nTraceback at FileHandler.java:42"
    res = parse_uploaded_file(content, "error.log")
    assert res["filename"] == "error.log"
    assert "NullPointerException" in res["logs"] or "NullPointerException" in res["description"]

def test_error_rectification_null_pointer():
    rec = generate_error_rectification(
        title="NullPointerException in FileHandler",
        description="Uploading large file causes NullPointerException",
        logs="java.lang.NullPointerException at FileHandler.java:42",
        category="Bug"
    )
    assert "Null Reference" in rec["root_cause"]
    assert len(rec["rectification_steps"]) > 0
    assert rec["recommended_code_fix"] is not None

def test_error_rectification_cors():
    rec = generate_error_rectification(
        title="CORS policy issue",
        description="Access to fetch from origin blocked by CORS policy",
        logs="Access-Control-Allow-Origin header missing",
        category="Question"
    )
    assert "CORS" in rec["root_cause"]
    assert len(rec["rectification_steps"]) > 0
