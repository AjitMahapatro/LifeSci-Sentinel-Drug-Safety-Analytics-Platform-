"""Shared pytest fixtures and path configuration.

Ensures the repository root is on sys.path so that `api` and `src` packages
are importable regardless of how pytest is invoked.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
