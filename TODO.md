# Deployment Implementation Checklist

## Docker + docker-compose deployment of LifeSci Sentinel

- [x] Create `docker/Dockerfile.api` — Python backend (wait-for-db, schema init, data load, uvicorn)
- [x] Create `docker/init/01_schema.sql` — warehouse schema + tables bootstrap (DDL missing from repo)
- [x] Create `docker/wait_for_db.py` — DB readiness helper used by backend entrypoint
- [x] Create `frontend/Dockerfile` — multi-stage Vite build served by nginx
- [x] Create `frontend/nginx.conf` — serve static build + proxy `/api` to FastAPI service
- [x] Create `docker-compose.yml` — db, api, frontend services, healthchecks, env wiring
- [x] Create `.dockerignore` — exclude lifescivenv, .git, node_modules, .env, logs, caches
- [x] Create/update `.env.example` — safe placeholders (DB, POSTGRES, CORS_ORIGINS, optional OPENAI)
- [x] Add optional `VITE_API_URL` support in `frontend/src/api.ts` (+ `vite-env.d.ts`)
- [x] Update `README.md` with Docker deployment instructions
- [x] Verify: `docker-compose.yml` is valid + frontend production build succeeds
- [x] Run existing test suite (43 tests) after deployment changes — `43 passed`
- [x] Run `docker compose up --build` on a machine with Docker installed — verified end-to-end
- [x] Fix: entrypoint passes `PGPASSWORD` to psql (non-interactive schema init)
- [x] Copy `tests/` into API image so the suite can run inside the container against the DB

