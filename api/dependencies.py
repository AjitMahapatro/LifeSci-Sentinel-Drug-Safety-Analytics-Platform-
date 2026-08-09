"""Shared FastAPI dependencies for the LifeSci Sentinel API."""

from __future__ import annotations

from fastapi import Depends

from api.services.database_service import (
    DatabaseService,
    get_database_service,
)
from api.services.ai_service import get_ai_service


def get_db() -> DatabaseService:
    """Provide the shared database service dependency."""
    return get_database_service()


def get_ai() -> object:
    """Provide the shared AI service dependency."""
    return get_ai_service()


__all__ = ["get_db", "get_ai", "DatabaseService", "Depends"]
