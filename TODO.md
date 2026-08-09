# LifeSci Sentinel — Implementation TODO

## Phase 1 — Reusable Analytics Service ✅ COMPLETE
- [x] Created `src/analytics/service.py` (reusable, type-hinted functions)
- [x] Created `config/risk_rules.json` (configurable LOW/MODERATE/HIGH/CRITICAL thresholds)
- [x] Verified: serious-rate, priority, risk classification functions

## Phase 2 — FastAPI ✅ COMPLETE
- [x] Created `api/main.py`, `dependencies.py`, `routes/`, `schemas/`, `services/`
- [x] Implemented endpoints: health, analytics (overview, trends), drugs, reactions, signals, investigation, ai
- [x] Endpoints verified: 16 required endpoints present

## Phase 3 — Signal Investigation ✅ COMPLETE
- [x] Implemented explainable investigation endpoint (real data + rationale + DQ status)

## Phase 4 — AI Assistant ✅ COMPLETE
- [x] Grounded intent engine + rule-based explanation (offline default)
- [x] Optional OpenAI-compatible LLM behind env flag
- [x] Read-only, SELECT-only, whitelisted SQL; destructive SQL blocked

## Phase 5 — React Frontend (Vite + TS + Tailwind) ✅ COMPLETE
- [x] 6 pages: Overview, Drug, Reaction, Signals, Signal Investigation, AI Assistant
- [x] Frontend production build verified (tsc + vite build passed)

## Phase 6 — Integration ✅ COMPLETE
- [x] React -> FastAPI -> Analytics -> PostgreSQL

## Phase 7 — Testing (pytest) ✅ COMPLETE
- [x] connection, serious-rate, priority, risk, services, endpoints, AI validation
- [x] 43 tests passing

## Phase 8 — Documentation ✅ COMPLETE
- [x] Rewrote README (overview, architecture, data engineering, warehouse, DQ, methodology, Power BI, FastAPI, React, AI, endpoints, setup, env, testing, limitations)
- [x] `.env.example` verified present
- [x] `requirements.txt` now includes scikit-learn, fastapi, uvicorn, pydantic, pytest, httpx

## Phase 9 — Final Review ✅ COMPLETE
- [x] Complete system audit performed
- [x] Frontend build verified
- [x] Test suite verified (43 passed)
- [x] Removed unnecessary artifacts (.pytest_cache, empty notebooks/, empty src/dq/)
- [x] Added .pytest_cache/ to .gitignore
