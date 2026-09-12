import os
import json
import datetime
from sqlalchemy.orm import Session
from backend.app.database.session import engine, Base, SessionLocal
from backend.app.models.db_models import IssueDB, ModelVersionDB, PredictionDB

def init_database():
    print("[DB] Creating database tables if not existing...")
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # 1. Seed Model Version if empty
        if db.query(ModelVersionDB).count() == 0:
            meta_path = "models/model_metadata.json"
            model_name = "Linear SVM"
            version = "v1.0.0"
            acc = 0.942
            macro_f1 = 0.941
            weighted_f1 = 0.942

            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        m_data = json.load(f)
                        model_name = m_data.get("model_name", model_name)
                        version = m_data.get("version", version)
                        acc = m_data.get("best_accuracy", acc)
                        macro_f1 = m_data.get("best_macro_f1", macro_f1)
                        weighted_f1 = m_data.get("best_macro_f1", weighted_f1)
                except Exception as e:
                    print(f"[DB] Note reading model_metadata: {e}")

            mv = ModelVersionDB(
                version=version,
                model_name=model_name,
                dataset_version="Kaggle GitHub Bugs Benchmark v1.0",
                accuracy=acc,
                macro_f1=macro_f1,
                weighted_f1=weighted_f1,
                status="active",
                created_at=datetime.datetime.utcnow()
            )
            db.add(mv)
            db.commit()
            print(f"[DB] Initialized model version record {version}")

        # 2. Seed Initial Benchmark Issues if empty
        if db.query(IssueDB).count() == 0:
            sample_issues = [
                {
                    "title": "Application crashes when uploading large PNG files",
                    "description": "Uploading images >5MB causes 500 internal server error with NullPointerException in FileHandler.java line 42.",
                    "predicted_category": "Bug",
                    "confidence": 0.942,
                    "is_low_confidence": False,
                    "quality_score": 85,
                    "priority_recommendation": "High",
                    "team_recommendation": "Backend",
                    "model_version": "v1.0.0",
                    "status": "open"
                },
                {
                    "title": "Add dark mode toggle to user settings page",
                    "description": "Users have requested a dark theme for night usage with automatic OS theme synchronization.",
                    "predicted_category": "Feature",
                    "confidence": 0.915,
                    "is_low_confidence": False,
                    "quality_score": 78,
                    "priority_recommendation": "Medium",
                    "team_recommendation": "Frontend",
                    "model_version": "v1.0.0",
                    "status": "open"
                },
                {
                    "title": "How can I configure JWT token expiration times?",
                    "description": "Where in config.yaml or environment variables can we change the default access token lifetime from 15 mins to 60 mins?",
                    "predicted_category": "Question",
                    "confidence": 0.887,
                    "is_low_confidence": False,
                    "quality_score": 72,
                    "priority_recommendation": "Low",
                    "team_recommendation": "Documentation",
                    "model_version": "v1.0.0",
                    "status": "open"
                },
                {
                    "title": "Database connection pool exhausted under spike load",
                    "description": "During peak traffic hours, DB throws OperationalError too many connections and times out.",
                    "predicted_category": "Bug",
                    "confidence": 0.582,
                    "is_low_confidence": True,
                    "quality_score": 65,
                    "priority_recommendation": "Critical",
                    "team_recommendation": "Database",
                    "model_version": "v1.0.0",
                    "status": "open"
                },
                {
                    "title": "Memory leak in WebSocket real-time issue streaming handler",
                    "description": "Long-running client WebSocket connections cause RAM memory usage to grow continuously until OOM killer terminates node process.",
                    "predicted_category": "Bug",
                    "confidence": 0.965,
                    "is_low_confidence": False,
                    "quality_score": 92,
                    "priority_recommendation": "Critical",
                    "team_recommendation": "Backend",
                    "model_version": "v1.0.0",
                    "status": "open"
                },
                {
                    "title": "Export issue triage reports to PDF and CSV format",
                    "description": "Engineering managers need an export button in the dashboard to download monthly classification summary report files.",
                    "predicted_category": "Feature",
                    "confidence": 0.931,
                    "is_low_confidence": False,
                    "quality_score": 88,
                    "priority_recommendation": "Medium",
                    "team_recommendation": "Frontend",
                    "model_version": "v1.0.0",
                    "status": "open"
                },
                {
                    "title": "How to execute database migrations inside Docker Compose startup?",
                    "description": "What is the recommended approach to run Alembic migration scripts automatically before starting the Uvicorn web server?",
                    "predicted_category": "Question",
                    "confidence": 0.894,
                    "is_low_confidence": False,
                    "quality_score": 80,
                    "priority_recommendation": "Low",
                    "team_recommendation": "DevOps",
                    "model_version": "v1.0.0",
                    "status": "open"
                },
                {
                    "title": "API rate limiter fails to block excessive login retry attempts",
                    "description": "Brute force requests on /api/v1/auth/login are not rate limited properly when proxy headers are forwarded.",
                    "predicted_category": "Bug",
                    "confidence": 0.928,
                    "is_low_confidence": False,
                    "quality_score": 89,
                    "priority_recommendation": "High",
                    "team_recommendation": "Security",
                    "model_version": "v1.0.0",
                    "status": "open"
                }
            ]

            for iss_data in sample_issues:
                issue = IssueDB(**iss_data)
                db.add(issue)
            db.commit()
            print("[DB] Initialized benchmark issues.")

    finally:
        db.close()

if __name__ == "__main__":
    init_database()
