#!/usr/bin/env bash
# LifeSci Sentinel API container entrypoint.
#
# 1. Wait for PostgreSQL to accept connections.
# 2. Apply the `warehouse` schema bootstrap SQL (idempotent).
# 3. Load gold-layer CSVs into the warehouse via the existing load_all pipeline.
# 4. Start uvicorn serving the FastAPI app.
#
# The seed/load step only runs automatically once (guarded by a marker) so that
# restarts do not repeatedly wipe and reload the tables. Set FORCE_SEED=1 to
# force a full reload on startup.

set -euo pipefail

echo "[entrypoint] Waiting for database..."
python docker/wait_for_db.py --timeout "${DB_WAIT_TIMEOUT:-90}"

# Apply schema if it does not already exist.
# PGPASSWORD is required for non-interactive psql authentication.
export PGPASSWORD="${DB_PASSWORD}"
echo "[entrypoint] Ensuring warehouse schema exists..."
psql -v ON_ERROR_STOP=1 \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -f docker/init/01_schema.sql
unset PGPASSWORD

SEED_MARKER="/app/.seed-complete"

should_seed() {
  if [[ "${FORCE_SEED:-0}" == "1" ]]; then
    return 0
  fi
  if [[ ! -f "$SEED_MARKER" ]]; then
    return 0
  fi
  return 1
}

if should_seed; then
  echo "[entrypoint] Loading gold data into warehouse..."
  python -m src.database.load_all
  echo "[entrypoint] Creating seed marker."
  touch "$SEED_MARKER"
else
  echo "[entrypoint] Data already seeded; skipping gold load."
fi

echo "[entrypoint] Starting API server..."
exec uvicorn api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers "${UVICORN_WORKERS:-1}" \
  "$@"
