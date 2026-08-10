"""Analytics, drugs, reactions, signals, and AI route endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from urllib.parse import unquote

from api.schemas.models import (
    AIQueryRequest,
    AIResponse,
    AnalyticsOverview,
    DrugInvestigation,
    DrugList,
    DrugReactions,
    ReactionInvestigation,
    ReactionList,
    SignalInvestigation,
    SignalList,
)
from api.services.database_service import (
    DatabaseService,
    get_database_service,
)
from api.services.ai_service import get_ai_service

router = APIRouter()


def _db() -> DatabaseService:
    return get_database_service()


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


@router.get("/analytics/overview", response_model=AnalyticsOverview)
def analytics_overview(db: DatabaseService = Depends(_db)) -> dict:
    try:
        return db.overview()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Analytics unavailable") from exc


@router.get("/analytics/trends")
def analytics_trends(db: DatabaseService = Depends(_db)) -> dict:
    try:
        overview = db.overview()
        return {"trends": overview.get("trends", [])}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Analytics unavailable") from exc


# ---------------------------------------------------------------------------
# Drugs
# ---------------------------------------------------------------------------


@router.get("/drugs", response_model=DrugList)
def list_drugs(
    search: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    min_reports: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: DatabaseService = Depends(_db),
) -> dict:
    try:
        return db.drug_list(
            search=search, risk_level=risk_level, min_reports=min_reports, limit=limit
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Drug data unavailable") from exc


@router.get("/drugs/{drug_name}", response_model=DrugInvestigation)
def get_drug(drug_name: str, db: DatabaseService = Depends(_db)) -> dict:
    detail = db.drug_detail(drug_name)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Drug '{drug_name}' not found")
    reactions = db.drug_reactions(drug_name)
    trends = db.drug_trends(drug_name)
    for t in trends:
        t["serious_rate"] = round(
            (
                int(t["serious_reports"]) / int(t["total_reports"])
                if int(t["total_reports"]) > 0
                else 0.0
            ),
            4,
        )
    signals = db.signals(limit=1000).get("signals", [])
    drug_signals = [s for s in signals if s["drug"] == drug_name]
    return {
        **detail,
        "top_reactions": reactions,
        "trends": trends,
        "signals": drug_signals,
    }


@router.get("/drugs/{drug_name}/reactions", response_model=DrugReactions)
def drug_reactions(drug_name: str, db: DatabaseService = Depends(_db)) -> dict:
    if not db.drug_detail(drug_name):
        raise HTTPException(status_code=404, detail=f"Drug '{drug_name}' not found")
    return {"drug_name": drug_name, "reactions": db.drug_reactions(drug_name)}


# ---------------------------------------------------------------------------
# Reactions
# ---------------------------------------------------------------------------


@router.get("/reactions", response_model=ReactionList)
def list_reactions(
    limit: int = Query(default=100, ge=1, le=1000),
    db: DatabaseService = Depends(_db),
) -> dict:
    try:
        return db.reaction_list(limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Reaction data unavailable") from exc


@router.get("/reactions/{reaction_name}", response_model=ReactionInvestigation)
def get_reaction(reaction_name: str, db: DatabaseService = Depends(_db)) -> dict:
    detail = db.reaction_detail(reaction_name)
    if not detail:
        raise HTTPException(
            status_code=404, detail=f"Reaction '{reaction_name}' not found"
        )
    return detail


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------


@router.get("/signals", response_model=SignalList)
def list_signals(
    risk_level: str | None = Query(default=None),
    min_reports: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: DatabaseService = Depends(_db),
) -> dict:
    try:
        return db.signals(
            risk_level=risk_level, min_reports=min_reports, limit=limit
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Signal data unavailable") from exc


@router.get("/signals/{drug_name}", response_model=SignalList)
def signals_for_drug(drug_name: str, db: DatabaseService = Depends(_db)) -> dict:
    # Path parameters may be percent-encoded by the frontend; decode here
    drug_name = unquote(drug_name)
    if not db.drug_detail(drug_name):
        raise HTTPException(status_code=404, detail=f"Drug '{drug_name}' not found")
    all_signals = db.signals(limit=1000).get("signals", [])
    filtered = [s for s in all_signals if s["drug"] == drug_name]
    return {"count": len(filtered), "signals": filtered}


@router.get("/signals/{drug_name}/{reaction_name}", response_model=SignalInvestigation)
def get_signal(
    drug_name: str, reaction_name: str, db: DatabaseService = Depends(_db)
) -> dict:
    # Decode percent-encoded path params to match DB values exactly
    drug_name = unquote(drug_name)
    reaction_name = unquote(reaction_name)
    detail = db.signal_detail(drug_name, reaction_name)
    if not detail:
        raise HTTPException(
            status_code=404,
            detail=f"Signal '{drug_name}' / '{reaction_name}' not found",
        )
    return detail


@router.get(
    "/signals/{drug_name}/{reaction_name}/investigation",
    response_model=SignalInvestigation,
)
def signal_investigation(
    drug_name: str, reaction_name: str, db: DatabaseService = Depends(_db)
) -> dict:
    # Decode percent-encoded path params to match DB values exactly
    drug_name = unquote(drug_name)
    reaction_name = unquote(reaction_name)
    detail = db.signal_detail(drug_name, reaction_name)
    if not detail:
        raise HTTPException(
            status_code=404,
            detail=f"Signal '{drug_name}' / '{reaction_name}' not found",
        )
    return detail


# ---------------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------------


@router.post("/ai/query", response_model=AIResponse)
def ai_query(request: AIQueryRequest) -> dict:
    if not request.question.strip():
        raise HTTPException(status_code=422, detail="Question cannot be empty")
    try:
        ai = get_ai_service()
        return ai.answer(
            question=request.question,
            drug=request.drug,
            reaction=request.reaction,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="AI service unavailable") from exc
