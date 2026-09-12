import os
import glob
import json
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Optional

LABEL_MAP = {
    0: "Bug",
    1: "Feature",
    2: "Question",
    "0": "Bug",
    "1": "Feature",
    "2": "Question",
    "bug": "Bug",
    "feature": "Feature",
    "question": "Question",
    "bugs": "Bug",
    "features": "Feature",
    "questions": "Question"
}

def detect_and_load_raw_data(raw_dir: str = "data/raw") -> Tuple[pd.DataFrame, Optional[pd.DataFrame], Dict[str, Any]]:
    """
    Scans raw_dir for dataset files (.json, .csv, .parquet), automatically detects format,
    inspects schema, maps Title/Body to combined text and maps Label to Bug/Feature/Question.
    If no raw data files are found, generates a representative standard benchmark dataset.
    """
    search_paths = [
        os.path.join(raw_dir, "**", "*.json"),
        os.path.join(raw_dir, "**", "*.csv"),
        os.path.join(raw_dir, "*.json"),
        os.path.join(raw_dir, "*.csv")
    ]
    
    found_files = []
    for pattern in search_paths:
        found_files.extend(glob.glob(pattern, recursive=True))
    
    # Filter out README files
    found_files = [f for f in found_files if not f.lower().endswith("readme.md")]
    
    train_df = None
    test_df = None
    source_info = {"status": "none", "files": []}

    if found_files:
        train_file = None
        test_file = None
        for f in found_files:
            fname = os.path.basename(f).lower()
            if "train" in fname:
                train_file = f
            elif "test" in fname:
                test_file = f
        
        if not train_file and len(found_files) > 0:
            train_file = found_files[0]

        if train_file:
            train_df = _read_and_standardize_file(train_file)
            source_info["train_file"] = train_file
            source_info["status"] = "found_raw"

        if test_file:
            test_df = _read_and_standardize_file(test_file)
            source_info["test_file"] = test_file

    if train_df is None or train_df.empty:
        print("[DatasetLoader] No raw Kaggle dataset found in data/raw/. Generating benchmark dataset...")
        train_df, test_df = generate_benchmark_dataset(raw_dir)
        source_info["status"] = "generated_benchmark"

    stats = analyze_dataset_statistics(train_df, test_df)
    return train_df, test_df, {**source_info, "stats": stats}

def _read_and_standardize_file(filepath: str) -> pd.DataFrame:
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        df = pd.read_json(filepath)
    elif ext == ".csv":
        df = pd.read_csv(filepath)
    elif ext == ".parquet":
        df = pd.read_parquet(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return standardize_schema(df)

def standardize_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes schema regardless of column casing or naming variations.
    Combines Title + Body -> text, maps target labels to Bug / Feature / Question.
    """
    cols_lower = {col.lower(): col for col in df.columns}

    # Identify Title column
    title_col = None
    for cand in ["title", "issue_title", "subject", "summary"]:
        if cand in cols_lower:
            title_col = cols_lower[cand]
            break

    # Identify Body column
    body_col = None
    for cand in ["body", "description", "issue_body", "text", "content"]:
        if cand in cols_lower:
            body_col = cols_lower[cand]
            break

    # Identify Label column
    label_col = None
    for cand in ["label", "target", "category", "class", "issue_type"]:
        if cand in cols_lower:
            label_col = cols_lower[cand]
            break

    df_clean = pd.DataFrame()
    
    # Handle text extraction
    if title_col and body_col:
        df_clean["title"] = df[title_col].fillna("").astype(str)
        df_clean["body"] = df[body_col].fillna("").astype(str)
        df_clean["text"] = df_clean["title"] + " " + df_clean["body"]
    elif title_col:
        df_clean["title"] = df[title_col].fillna("").astype(str)
        df_clean["body"] = ""
        df_clean["text"] = df_clean["title"]
    elif body_col:
        df_clean["title"] = ""
        df_clean["body"] = df[body_col].fillna("").astype(str)
        df_clean["text"] = df_clean["body"]
    elif "text" in cols_lower:
        df_clean["text"] = df[cols_lower["text"]].fillna("").astype(str)
        df_clean["title"] = df_clean["text"].apply(lambda t: t[:50])
        df_clean["body"] = df_clean["text"]
    else:
        # Fallback: concatenate all text columns
        text_cols = [c for c in df.columns if df[c].dtype == "object"]
        df_clean["text"] = df[text_cols].fillna("").astype(str).agg(" ".join, axis=1)
        df_clean["title"] = df_clean["text"].apply(lambda t: t[:50])
        df_clean["body"] = df_clean["text"]

    # Standardize label
    if label_col:
        df_clean["label_raw"] = df[label_col]
        df_clean["label"] = df[label_col].apply(_map_label)
    else:
        df_clean["label"] = None

    return df_clean

def _map_label(val: Any) -> str:
    if pd.isna(val):
        return "Unknown"
    
    # String mapping
    val_str = str(val).strip()
    if val_str in LABEL_MAP:
        return LABEL_MAP[val_str]
    if val_str.lower() in LABEL_MAP:
        return LABEL_MAP[val_str.lower()]
    
    # Int mapping
    try:
        val_int = int(float(val_str))
        if val_int in LABEL_MAP:
            return LABEL_MAP[val_int]
    except ValueError:
        pass
        
    return val_str.capitalize()

def analyze_dataset_statistics(train_df: pd.DataFrame, test_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    stats = {
        "train_rows": len(train_df),
        "test_rows": len(test_df) if test_df is not None else 0,
        "columns": list(train_df.columns),
        "missing_text_count": int(train_df["text"].str.strip().eq("").sum()),
        "duplicate_rows": int(train_df.duplicated(subset=["text"]).sum()),
    }
    
    if "label" in train_df and train_df["label"].notna().any():
        stats["class_distribution"] = train_df["label"].value_counts().to_dict()
        stats["class_percentages"] = (train_df["label"].value_counts(normalize=True) * 100).round(2).to_dict()
        
        # Calculate length distribution per class
        train_df["char_len"] = train_df["text"].str.len()
        train_df["word_count"] = train_df["text"].apply(lambda x: len(x.split()))
        
        stats["avg_word_count_by_class"] = train_df.groupby("label")["word_count"].mean().round(1).to_dict()
        stats["avg_char_count_by_class"] = train_df.groupby("label")["char_len"].mean().round(1).to_dict()
        stats["overall_avg_word_count"] = float(train_df["word_count"].mean())
        stats["overall_avg_char_count"] = float(train_df["char_len"].mean())

    return stats

def generate_benchmark_dataset(output_dir: str = "data/raw") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Generates a rich, realistic software issues benchmark dataset across Bug, Feature, and Question classes."""
    os.makedirs(output_dir, exist_ok=True)
    
    bug_templates = [
        ("Application crashes on file upload", "When uploading a large PNG file (>5MB), the system throws NullPointerException at FileHandler.java:42. Stacktrace attached. System freezes completely."),
        ("Unhandled exception in API authentication pipeline", "POST /api/v1/auth/login returns 500 Internal Server Error when OAuth token expires. Traceback: KeyError: 'expires_in' in auth_service.py line 88."),
        ("Database connection pool exhausted during high load", "Under heavy load, DB connection fails with 'OperationalError: too many connections'. Pool size max is reached and requests timeout after 30 seconds."),
        ("Memory leak in background task worker process", "Celery worker RAM consumption increases continuously by ~50MB per hour. Memory is not released after image processing jobs complete."),
        ("Form validation fails silently on user signup", "Submitting signup form with trailing spaces in email address fails validation without displaying an error message to the user."),
        ("JSON payload parsing error in Webhook handler", "Stripe webhook endpoint throws 400 Bad Request error when payload contains special unicode characters. Invalid UTF-8 byte sequence."),
        ("UI layout breaks on mobile viewport", "Navbar overlaps with dashboard cards on screen width < 768px. Flexbox grid container overflow is not handled properly in CSS."),
        ("Infinite loop when rendering nested comments", "Component re-renders continuously when comment depth > 5. Causes browser tab to freeze and crash with Out Of Memory error."),
        ("Session token persists after logout request", "Calling POST /auth/logout clears local storage but server JWT token remains active and valid until expiration. Security vulnerability."),
        ("Export to CSV fails when dataframe contains nulls", "Clicking export button causes AttributeError: 'NoneType' object has no attribute 'encode'. Occurs when dataset rows contain NULL fields.")
    ]

    feature_templates = [
        ("Add dark mode toggle to navigation header", "Please add dark mode support with system theme synchronization and persistence in local storage across browser sessions."),
        ("Support OAuth2 authentication via GitHub and Google", "Users should be able to log in using GitHub or Google SSO. Implement OAuth2 flow with automatic user profile creation."),
        ("Implement PDF export option for analytics report", "Allow users to export weekly analytics reports as downloadable PDF files with customizable chart filters and date ranges."),
        ("Add drag-and-drop file upload interface", "Replace static file input field with a modern drag-and-drop zone supporting multi-file uploads and real-time upload progress bars."),
        ("Provide REST API rate limiting per user key", "Implement sliding window rate limiting for public API endpoints. Users should receive HTTP 429 Too Many Requests when exceeding rate limits."),
        ("Add multi-language localization (i18n) support", "Integrate react-i18next framework to allow switching UI text between English, Spanish, French, and German."),
        ("Enable bulk action export for selected database rows", "Add checkbox select-all option to tables to permit bulk deletion, export, and status modification of selected records."),
        ("Implement real-time WebSocket notifications for events", "Notify logged-in users instantly when an issue state changes or when they are mentioned in a comment."),
        ("Support webhook integrations for Slack and Discord", "Allow repository administrators to configure custom webhooks to receive alert notifications in Slack or Discord channels."),
        ("Add command palette (Ctrl+K) for quick navigation", "Implement a global search keyboard shortcut palette allowing quick jump to issues, settings, and documentation pages.")
    ]

    question_templates = [
        ("How do I configure custom database connection timeouts?", "Where in config.yaml or environment variables can I set max DB connection timeout for PostgreSQL background tasks?"),
        ("What is the recommended deployment pattern for Kubernetes?", "Is there an official Helm chart or manifest example for deploying DevLens behind an NGINX ingress controller?"),
        ("How to handle pagination in REST API GET /issues?", "What query parameters are supported for page size and cursor-based pagination? Does the response return total page count?"),
        ("Which Python versions are officially supported by devlens-core?", "Documentation mentions Python 3.10+, but does it run stably on Python 3.14? Are there C-extension compatibility issues?"),
        ("How to override default TF-IDF max_features in training pipeline?", "I want to train the issue classifier with max_features=25000. How can I pass custom vectorizer parameters to train.py?"),
        ("Is there a rate limit on the issue triage endpoint?", "What are the default rate limits for POST /api/v1/triage? Can we configure higher limits for internal CI pipelines?"),
        ("How to integrate custom LDAP server for enterprise auth?", "Are there configuration docs for configuring LDAP domain controller authentication alongside standard JWT tokens?"),
        ("Where are model training metrics and artifacts saved?", "Does the training pipeline store model version metadata in SQLite by default, or is PostgreSQL required?"),
        ("How to configure CORS headers for frontend frontend domain?", "Getting CORS blocked error when requesting backend from custom domain. Which setting controls CORS origins?"),
        ("Can DevLens detect duplicate issues across multiple repositories?", "Does similarity search work globally across all repos or only within the scope of a single selected project repository?")
    ]

    np.random.seed(42)
    records = []
    
    # Generate 1500 dataset records
    for i in range(1500):
        cls_idx = i % 3
        if cls_idx == 0:
            title_tpl, body_tpl = bug_templates[i % len(bug_templates)]
            lbl_raw = 0
            lbl_str = "Bug"
        elif cls_idx == 1:
            title_tpl, body_tpl = feature_templates[i % len(feature_templates)]
            lbl_raw = 1
            lbl_str = "Feature"
        else:
            title_tpl, body_tpl = question_templates[i % len(question_templates)]
            lbl_raw = 2
            lbl_str = "Question"

        # Add natural variation
        variations_title = [
            f"{title_tpl}",
            f"[Issue #{1000+i}] {title_tpl}",
            f"[{lbl_str.upper()}] {title_tpl}",
            f"Request: {title_tpl}"
        ]
        
        selected_title = variations_title[i % len(variations_title)]
        selected_body = f"{body_tpl} (Ref ID: {10000+i}. System context build {i % 10})."
        
        records.append({
            "Title": selected_title,
            "Body": selected_body,
            "Label": lbl_raw,
            "label": lbl_str,
            "title": selected_title,
            "body": selected_body,
            "text": f"{selected_title} {selected_body}"
        })

    full_df = pd.DataFrame(records)
    
    # Split 80/20 train/test
    train_size = int(len(full_df) * 0.8)
    train_df = full_df.iloc[:train_size].copy()
    test_df = full_df.iloc[train_size:].copy()

    # Save to data/raw for instant usability
    train_df[["Title", "Body", "Label"]].to_csv(os.path.join(output_dir, "train.csv"), index=False)
    test_df[["Title", "Body", "Label"]].to_csv(os.path.join(output_dir, "test.csv"), index=False)

    print(f"[DatasetLoader] Benchmark dataset created: {len(train_df)} train samples, {len(test_df)} test samples.")
    return train_df, test_df

if __name__ == "__main__":
    tr, te, inf = detect_and_load_raw_data()
    print("Dataset Status:", inf["status"])
    print("Train Shape:", tr.shape)
    print("Stats:", json.dumps(inf["stats"], indent=2))
