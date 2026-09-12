from fastapi import APIRouter
from backend.app.api.endpoints.issues import router as issues_router

api_router = APIRouter()
api_router.include_router(issues_router, tags=["DevLens AI Core Platform API"])
