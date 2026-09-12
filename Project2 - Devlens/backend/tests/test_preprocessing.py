import pytest
from ml.preprocessing import TextPreprocessor

def test_lowercase_and_whitespace():
    prep = TextPreprocessor(lowercase=True, remove_stopwords=False)
    raw = "  Application   CRASHES  When Uploading   File!  "
    clean = prep.preprocess_text(raw)
    assert "application crashes when uploading" in clean

def test_stopword_removal():
    prep = TextPreprocessor(lowercase=True, remove_stopwords=True, remove_punctuation=True)
    raw = "How can I configure authentication for the REST API?"
    clean = prep.preprocess_text(raw)
    tokens = clean.split()
    assert "configure" in tokens
    assert "authentication" in tokens
    assert "rest" in tokens
    assert "api" in tokens
    assert "how" not in tokens
    assert "the" not in tokens

def test_empty_string_handling():
    prep = TextPreprocessor()
    assert prep.preprocess_text(None) == ""
    assert prep.preprocess_text("") == ""
    assert prep.preprocess_text("   ") == ""
