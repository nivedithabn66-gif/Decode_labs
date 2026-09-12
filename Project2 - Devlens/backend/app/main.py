import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.api.router import api_router
from backend.app.database.init_db import init_database
from ml.predict import get_issue_predictor

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("DevLensAPI")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[DevLens] Initializing database connection & tables...")
    init_database()
    logger.info("[DevLens] Pre-loading ML Classifier model into memory...")
    get_issue_predictor()
    logger.info("[DevLens] DevLens Backend Service started successfully.")
    yield
    logger.info("[DevLens] DevLens Backend Service shutting down.")

app = FastAPI(
    title="DevLens AI Platform API",
    description="AI-Powered GitHub Issue Classification & Intelligent Developer Triage Platform (DecodeLabs AI Project 2)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Exception caught: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An internal server error occurred.",
            "detail": str(exc)
        }
    )

# Include API Routers (/api and /api/v1)
app.include_router(api_router, prefix="/api")
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def root():
    return {
        "service": "DevLens AI Platform API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["Health Check"])
def health_root():
    return {
        "status": "healthy",
        "api_status": "Operational",
        "database": "Connected",
        "ml_model": "Loaded"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
