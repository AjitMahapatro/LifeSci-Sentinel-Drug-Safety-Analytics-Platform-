"""FastAPI application entrypoint for LifeSci Sentinel.

Run with:
    uvicorn api.main:app --reload
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.analytics import router as analytics_router
from api.services.database_service import get_database_service

load_dotenv()

app = FastAPI(
    title="LifeSci Sentinel API",
    description="Drug-safety intelligence platform API built on real-world "
    "pharmacovigilance data from OpenFDA/FAERS.",
    version="1.0.0",
)

# CORS configuration (frontend served from Vite dev server).
cors_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health() -> dict:
    """Health check returning API and database status."""
    db = get_database_service()
    db_status = db.health()
    return {
        "status": "ok" if db_status["status"] == "ok" else "degraded",
        "api": "running",
        "database": db_status,
    }


app.include_router(analytics_router, prefix="/api", tags=["analytics"])
