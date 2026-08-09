"""Pydantic response/request models for the LifeSci Sentinel API."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class HealthStatus(BaseModel):
    status: str
    database: str
    tables: int = 0


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


class Overview(BaseModel):
    total_reports: int
    total_drugs: int
    total_reactions: int
    serious_reports: int
    serious_rate: float


class TrendPoint(BaseModel):
    date_key: int
    year: int
    month: int
    month_name: str
    total_reports: int
    serious_reports: int
    serious_rate: float


class TopItem(BaseModel):
    name: str
    count: int


class AnalyticsOverview(BaseModel):
    summary: Overview
    top_drugs: list[TopItem]
    top_reactions: list[TopItem]
    trends: list[TrendPoint]


# ---------------------------------------------------------------------------
# Drugs
# ---------------------------------------------------------------------------


class RiskInfo(BaseModel):
    risk_level: str
    rationale: list[str]


class DrugSummary(BaseModel):
    drug_name: str
    total_reports: int
    serious_reports: int
    serious_rate: float
    priority_score: float
    priority_level: str
    risk: RiskInfo


class DrugList(BaseModel):
    count: int
    drugs: list[DrugSummary]


class ReactionDetail(BaseModel):
    reaction_name: str
    count: int


class DrugReactions(BaseModel):
    drug_name: str
    reactions: list[ReactionDetail]


class DrugInvestigation(BaseModel):
    drug_name: str
    total_reports: int
    serious_reports: int
    serious_rate: float
    priority_score: float
    priority_level: str
    risk: RiskInfo
    top_reactions: list[ReactionDetail]
    trends: list[TrendPoint]
    signals: list[dict[str, Any]]


# ---------------------------------------------------------------------------
# Reactions
# ---------------------------------------------------------------------------


class ReactionSummary(BaseModel):
    reaction_name: str
    total_reports: int
    serious_reports: int
    serious_rate: float
    affected_drugs: int


class ReactionList(BaseModel):
    count: int
    reactions: list[ReactionSummary]


class ReactionInvestigation(BaseModel):
    reaction_name: str
    total_reports: int
    serious_reports: int
    serious_rate: float
    affected_drugs: int
    top_drugs: list[TopItem]
    severity_distribution: dict[str, int]


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------


class SignalRow(BaseModel):
    drug: str
    reaction: str
    reports: int
    serious_reports: int
    serious_rate: float
    priority_score: float
    risk_level: str


class SignalList(BaseModel):
    count: int
    signals: list[SignalRow]


class SignalInvestigation(BaseModel):
    drug: str
    reaction: str
    risk_level: str
    priority_score: float
    reports: int
    serious_reports: int
    serious_rate: float
    reporting_trend: list[TrendPoint]
    associated_reactions: list[TopItem]
    associated_drugs: list[TopItem]
    data_quality: dict[str, Any]
    rationale: list[str]


# ---------------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------------


class AIQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    drug: Optional[str] = None
    reaction: Optional[str] = None


class AISource(BaseModel):
    type: Literal["database_analytics", "document_knowledge"]
    description: str


class AIResponse(BaseModel):
    answer: str
    evidence: list[dict[str, Any]]
    sources: list[AISource]
    question: str


class ErrorResponse(BaseModel):
    detail: str
