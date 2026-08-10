"""Wait-for-database helper.

Polls the PostgreSQL server until it is ready to accept connections, or until
a timeout elapses. Used by the API container entrypoint so the API does not
start before the database and schema are available.

Usage:
    python docker/wait_for_db.py [--timeout 60]
"""

from __future__ import annotations

import argparse
import os
import sys
import time

import psycopg2


def _conn_params() -> dict:
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "postgres"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
    }


def wait(timeout: int = 60) -> None:
    params = _conn_params()
    deadline = time.time() + timeout
    delay = 1.0
    while time.time() < deadline:
        try:
            conn = psycopg2.connect(**params)
            conn.close()
            print("Database is ready.", flush=True)
            return
        except psycopg2.OperationalError as exc:
            print(f"Database not ready ({exc}); retrying in {delay:.0f}s...", flush=True)
            time.sleep(delay)
            delay = min(delay + 1.0, 5.0)
    print(f"ERROR: Database did not become ready within {timeout}s.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()
    wait(args.timeout)
