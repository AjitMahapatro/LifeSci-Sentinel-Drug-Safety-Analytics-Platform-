"""Database repository service for the LifeSci Sentinel API.

This service queries the PostgreSQL warehouse (the authoritative data source used
by the existing Power BI analytics). It uses parameterized SQL and never exposes
raw database exceptions to callers.

It reuses the existing connection utility from src/database/connection.py.
"""

from __future__ import annotations

from typing import Any, Optional

import psycopg2
import psycopg2.extras

from src.database.connection import get_connection

from src.analytics import service as analytics_service


class DatabaseService:
    """Encapsulates read-only queries against the warehouse schema."""

    def __init__(self) -> None:
        self._conn: Optional[psycopg2.extensions.connection] = None

    def _connect(self) -> psycopg2.extensions.connection:
        if self._conn is None or self._conn.closed:
            self._conn = get_connection()
        return self._conn

    def _query(self, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        conn = self._connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]

    def _query_one(self, sql: str, params: tuple = ()) -> Optional[dict[str, Any]]:
        rows = self._query(sql, params)
        return rows[0] if rows else None

    def close(self) -> None:
        if self._conn is not None and not self._conn.closed:
            self._conn.close()
        self._conn = None

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health(self) -> dict[str, Any]:
        try:
            rows = self._query(
                """
                SELECT count(*) AS table_count
                FROM information_schema.tables
                WHERE table_schema = 'warehouse'
                """
            )
            table_count = int(rows[0]["table_count"]) if rows else 0
            return {"status": "ok", "database": "connected", "tables": table_count}
        except Exception:
            return {"status": "error", "database": "unavailable", "tables": 0}

    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------

    def overview(self) -> dict[str, Any]:
        summary_row = self._query_one(
            """
            SELECT
              COUNT(DISTINCT f.event_id)                             AS total_reports,
              COUNT(DISTINCT f.drug_key)                             AS total_drugs,
              COUNT(DISTINCT r.reaction_key)                         AS total_reactions,
              COUNT(DISTINCT CASE WHEN f.serious = 1 THEN f.event_id END)
                                                                      AS serious_reports
            FROM warehouse.fact_drug_safety_events f
            LEFT JOIN warehouse.fact_event_reaction fer ON fer.event_id = f.event_id
            LEFT JOIN warehouse.dim_reaction r ON r.reaction_key = fer.reaction_key
            """
        )
        if not summary_row:
            return {
                "summary": {
                    "total_reports": 0,
                    "total_drugs": 0,
                    "total_reactions": 0,
                    "serious_reports": 0,
                    "serious_rate": 0.0,
                },
                "top_drugs": [],
                "top_reactions": [],
                "trends": [],
            }
        total_reports = int(summary_row["total_reports"])
        serious_reports = int(summary_row["serious_reports"])
        summary = {
            "total_reports": total_reports,
            "total_drugs": int(summary_row["total_drugs"]),
            "total_reactions": int(summary_row["total_reactions"]),
            "serious_reports": serious_reports,
            "serious_rate": round(
                analytics_service.serious_rate(serious_reports, total_reports), 4
            ),
        }
        top_drugs = self._query(
            """
            SELECT d.drug_name AS name, COUNT(*) AS count
            FROM warehouse.fact_drug_safety_events f
            JOIN warehouse.dim_drug d ON d.drug_key = f.drug_key
            GROUP BY d.drug_name
            ORDER BY count DESC
            LIMIT 10
            """
        )
        top_reactions = self._query(
            """
            SELECT r.reaction_name AS name, COUNT(*) AS count
            FROM warehouse.fact_event_reaction fer
            JOIN warehouse.dim_reaction r ON r.reaction_key = fer.reaction_key
            GROUP BY r.reaction_name
            ORDER BY count DESC
            LIMIT 10
            """
        )
        trends = self._query(
            """
            SELECT
              f.date_key,
              dd.year,
              dd.month,
              dd.month_name,
              COUNT(*) AS total_reports,
              COUNT(CASE WHEN f.serious = 1 THEN 1 END) AS serious_reports
            FROM warehouse.fact_drug_safety_events f
            JOIN warehouse.dim_date dd ON dd.date_key = f.date_key
            GROUP BY f.date_key, dd.year, dd.month, dd.month_name
            ORDER BY f.date_key ASC
            """
        )
        for t in trends:
            total = int(t["total_reports"])
            serious = int(t["serious_reports"])
            t["serious_rate"] = round(
                analytics_service.serious_rate(serious, total), 4
            )
        return {
            "summary": summary,
            "top_drugs": top_drugs,
            "top_reactions": top_reactions,
            "trends": trends,
        }

    # ------------------------------------------------------------------
    # Drugs
    # ------------------------------------------------------------------

    def drug_list(
        self,
        search: Optional[str] = None,
        risk_level: Optional[str] = None,
        min_reports: int = 0,
        limit: int = 100,
    ) -> dict[str, Any]:
        where: list[str] = []
        params: list[Any] = []

        if search:
            where.append("d.drug_name ILIKE %s")
            params.append(f"%{search}%")

        where_sql = ("WHERE " + " AND ".join(where)) if where else ""

        rows = self._query(
            f"""
            SELECT
              d.drug_name,
              COUNT(*) AS total_reports,
              COUNT(CASE WHEN f.serious = 1 THEN 1 END) AS serious_reports
            FROM warehouse.fact_drug_safety_events f
            JOIN warehouse.dim_drug d ON d.drug_key = f.drug_key
            {where_sql}
            GROUP BY d.drug_name
            ORDER BY total_reports DESC
            LIMIT %s
            """,
            tuple(params) + (limit,),
        )

        priority = self._priority_map()
        drugs = []
        for row in rows:
            drug_name = row["drug_name"]
            total = int(row["total_reports"])
            serious = int(row["serious_reports"])
            sr = analytics_service.serious_rate(serious, total)
            p = priority.get(drug_name)
            score = float(p["priority_score"]) if p else 0.0
            existing_level = str(p["priority_level"]) if p else "Low"
            risk = analytics_service.classify_risk(score, sr, total)
            if risk_level and risk["risk_level"] != risk_level.upper():
                continue
            drugs.append(
                {
                    "drug_name": drug_name,
                    "total_reports": total,
                    "serious_reports": serious,
                    "serious_rate": round(sr, 4),
                    "priority_score": score,
                    "priority_level": existing_level,
                    "risk": risk,
                }
            )
        return {"count": len(drugs), "drugs": drugs}

    def _priority_map(self) -> dict[str, dict[str, Any]]:
        try:
            df = analytics_service.load_priority_scores()
            return {
                str(row["drug_name"]): {
                    "priority_score": float(row["priority_score"]),
                    "priority_level": str(row["priority_level"]),
                }
                for _, row in df.iterrows()
            }
        except Exception:
            return {}

    def drug_detail(self, drug_name: str) -> Optional[dict[str, Any]]:
        row = self._query_one(
            """
            SELECT
              d.drug_name,
              COUNT(*) AS total_reports,
              COUNT(CASE WHEN f.serious = 1 THEN 1 END) AS serious_reports
            FROM warehouse.fact_drug_safety_events f
            JOIN warehouse.dim_drug d ON d.drug_key = f.drug_key
            WHERE d.drug_name = %s
            GROUP BY d.drug_name
            """,
            (drug_name,),
        )
        if not row:
            return None
        total = int(row["total_reports"])
        serious = int(row["serious_reports"])
        sr = analytics_service.serious_rate(serious, total)
        p = self._priority_map().get(drug_name, {})
        score = float(p.get("priority_score", 0.0))
        existing_level = str(p.get("priority_level", "Low"))
        risk = analytics_service.classify_risk(score, sr, total)
        return {
            "drug_name": drug_name,
            "total_reports": total,
            "serious_reports": serious,
            "serious_rate": round(sr, 4),
            "priority_score": score,
            "priority_level": existing_level,
            "risk": risk,
        }

    def drug_reactions(self, drug_name: str) -> list[dict[str, Any]]:
        return self._query(
            """
            SELECT r.reaction_name, COUNT(*) AS count
            FROM warehouse.fact_drug_safety_events f
            JOIN warehouse.dim_drug d ON d.drug_key = f.drug_key
            JOIN warehouse.fact_event_reaction fer ON fer.event_id = f.event_id
            JOIN warehouse.dim_reaction r ON r.reaction_key = fer.reaction_key
            WHERE d.drug_name = %s
            GROUP BY r.reaction_name
            ORDER BY count DESC
            """,
            (drug_name,),
        )

    def drug_trends(self, drug_name: str) -> list[dict[str, Any]]:
        return self._query(
            """
            SELECT
              f.date_key,
              dd.year,
              dd.month,
              dd.month_name,
              COUNT(*) AS total_reports,
              COUNT(CASE WHEN f.serious = 1 THEN 1 END) AS serious_reports
            FROM warehouse.fact_drug_safety_events f
            JOIN warehouse.dim_drug d ON d.drug_key = f.drug_key
            JOIN warehouse.dim_date dd ON dd.date_key = f.date_key
            WHERE d.drug_name = %s
            GROUP BY f.date_key, dd.year, dd.month, dd.month_name
            ORDER BY f.date_key ASC
            """,
            (drug_name,),
        )

    # ------------------------------------------------------------------
    # Reactions
    # ------------------------------------------------------------------

    def reaction_list(self, limit: int = 100) -> dict[str, Any]:
        rows = self._query(
            """
            SELECT
              r.reaction_name,
              COUNT(DISTINCT f.event_id) AS total_reports,
              COUNT(DISTINCT CASE WHEN f.serious = 1 THEN f.event_id END)
                AS serious_reports,
              COUNT(DISTINCT f.drug_key) AS affected_drugs
            FROM warehouse.fact_event_reaction fer
            JOIN warehouse.dim_reaction r ON r.reaction_key = fer.reaction_key
            JOIN warehouse.fact_drug_safety_events f ON f.event_id = fer.event_id
            GROUP BY r.reaction_name
            ORDER BY total_reports DESC
            LIMIT %s
            """,
            (limit,),
        )
        for row in rows:
            total = int(row["total_reports"])
            serious = int(row["serious_reports"])
            row["serious_rate"] = round(
                analytics_service.serious_rate(serious, total), 4
            )
        return {"count": len(rows), "reactions": rows}

    def reaction_detail(self, reaction_name: str) -> Optional[dict[str, Any]]:
        row = self._query_one(
            """
            SELECT
              r.reaction_name,
              COUNT(DISTINCT f.event_id) AS total_reports,
              COUNT(DISTINCT CASE WHEN f.serious = 1 THEN f.event_id END)
                AS serious_reports,
              COUNT(DISTINCT f.drug_key) AS affected_drugs
            FROM warehouse.fact_event_reaction fer
            JOIN warehouse.dim_reaction r ON r.reaction_key = fer.reaction_key
            JOIN warehouse.fact_drug_safety_events f ON f.event_id = fer.event_id
            WHERE r.reaction_name = %s
            GROUP BY r.reaction_name
            """,
            (reaction_name,),
        )
        if not row:
            return None
        total = int(row["total_reports"])
        serious = int(row["serious_reports"])
        row["serious_rate"] = round(
            analytics_service.serious_rate(serious, total), 4
        )
        row["top_drugs"] = self._query(
            """
            SELECT d.drug_name AS name, COUNT(*) AS count
            FROM warehouse.fact_event_reaction fer
            JOIN warehouse.dim_reaction r ON r.reaction_key = fer.reaction_key
            JOIN warehouse.fact_drug_safety_events f ON f.event_id = fer.event_id
            JOIN warehouse.dim_drug d ON d.drug_key = f.drug_key
            WHERE r.reaction_name = %s
            GROUP BY d.drug_name
            ORDER BY count DESC
            LIMIT 10
            """,
            (reaction_name,),
        )
        sev = self._query(
            """
            SELECT
              CASE WHEN f.serious = 1 THEN 'serious' ELSE 'non_serious' END AS sev,
              COUNT(DISTINCT f.event_id) AS cnt
            FROM warehouse.fact_event_reaction fer
            JOIN warehouse.dim_reaction r ON r.reaction_key = fer.reaction_key
            JOIN warehouse.fact_drug_safety_events f ON f.event_id = fer.event_id
            WHERE r.reaction_name = %s
            GROUP BY sev
            """,
            (reaction_name,),
        )
        row["severity_distribution"] = {s["sev"]: int(s["cnt"]) for s in sev}
        return row

    # ------------------------------------------------------------------
    # Signals
    # ------------------------------------------------------------------

    def signals(
        self,
        risk_level: Optional[str] = None,
        min_reports: int = 0,
        limit: int = 100,
    ) -> dict[str, Any]:
        where: list[str] = []
        params: list[Any] = []
        if min_reports and min_reports > 0:
            where.append("COUNT(*) >= %s")
            params.append(min_reports)
        having_sql = ("HAVING " + " AND ".join(where)) if where else ""

        rows = self._query(
            f"""
            SELECT
              d.drug_name AS drug,
              r.reaction_name AS reaction,
              COUNT(*) AS reports,
              COUNT(CASE WHEN f.serious = 1 THEN 1 END) AS serious_reports
            FROM warehouse.fact_drug_safety_events f
            JOIN warehouse.dim_drug d ON d.drug_key = f.drug_key
            JOIN warehouse.fact_event_reaction fer ON fer.event_id = f.event_id
            JOIN warehouse.dim_reaction r ON r.reaction_key = fer.reaction_key
            GROUP BY d.drug_name, r.reaction_name
            {having_sql}
            ORDER BY reports DESC
            LIMIT %s
            """,
            tuple(params) + (limit,),
        )
        priority = self._priority_map()
        signals = []
        for row in rows:
            total = int(row["reports"])
            serious = int(row["serious_reports"])
            sr = analytics_service.serious_rate(serious, total)
            p = priority.get(row["drug"])
            score = float(p["priority_score"]) if p else 0.0
            risk = analytics_service.classify_risk(score, sr, total)
            if risk_level and risk["risk_level"] != risk_level.upper():
                continue
            signals.append(
                {
                    "drug": row["drug"],
                    "reaction": row["reaction"],
                    "reports": total,
                    "serious_reports": serious,
                    "serious_rate": round(sr, 4),
                    "priority_score": score,
                    "risk_level": risk["risk_level"],
                }
            )
        return {"count": len(signals), "signals": signals}

    def signal_detail(
        self, drug_name: str, reaction_name: str
    ) -> Optional[dict[str, Any]]:
        row = self._query_one(
            """
            SELECT
              d.drug_name AS drug,
              r.reaction_name AS reaction,
              COUNT(*) AS reports,
              COUNT(CASE WHEN f.serious = 1 THEN 1 END) AS serious_reports
            FROM warehouse.fact_drug_safety_events f
            JOIN warehouse.dim_drug d ON d.drug_key = f.drug_key
            JOIN warehouse.fact_event_reaction fer ON fer.event_id = f.event_id
            JOIN warehouse.dim_reaction r ON r.reaction_key = fer.reaction_key
            WHERE d.drug_name = %s AND r.reaction_name = %s
            GROUP BY d.drug_name, r.reaction_name
            """,
            (drug_name, reaction_name),
        )
        if not row:
            return None
        total = int(row["reports"])
        serious = int(row["serious_reports"])
        sr = analytics_service.serious_rate(serious, total)
        p = self._priority_map().get(row["drug"], {})
        score = float(p.get("priority_score", 0.0))
        risk = analytics_service.classify_risk(score, sr, total)

        trend = self._query(
            """
            SELECT
              f.date_key,
              dd.year,
              dd.month,
              dd.month_name,
              COUNT(*) AS total_reports,
              COUNT(CASE WHEN f.serious = 1 THEN 1 END) AS serious_reports
            FROM warehouse.fact_drug_safety_events f
            JOIN warehouse.dim_drug d ON d.drug_key = f.drug_key
            JOIN warehouse.fact_event_reaction fer ON fer.event_id = f.event_id
            JOIN warehouse.dim_reaction r ON r.reaction_key = fer.reaction_key
            JOIN warehouse.dim_date dd ON dd.date_key = f.date_key
            WHERE d.drug_name = %s AND r.reaction_name = %s
            GROUP BY f.date_key, dd.year, dd.month, dd.month_name
            ORDER BY f.date_key ASC
            """,
            (drug_name, reaction_name),
        )
        for t in trend:
            t["serious_rate"] = round(
                analytics_service.serious_rate(
                    int(t["serious_reports"]), int(t["total_reports"])
                ),
                4,
            )

        associated_reactions = self._query(
            """
            SELECT r2.reaction_name AS name, COUNT(*) AS count
            FROM warehouse.fact_drug_safety_events f
            JOIN warehouse.dim_drug d ON d.drug_key = f.drug_key
            JOIN warehouse.fact_event_reaction fer ON fer.event_id = f.event_id
            JOIN warehouse.dim_reaction r2 ON r2.reaction_key = fer.reaction_key
            WHERE d.drug_name = %s AND r2.reaction_name <> %s
            GROUP BY r2.reaction_name
            ORDER BY count DESC
            LIMIT 10
            """,
            (drug_name, reaction_name),
        )

        associated_drugs = self._query(
            """
            SELECT d2.drug_name AS name, COUNT(*) AS count
            FROM warehouse.fact_event_reaction fer
            JOIN warehouse.dim_reaction r ON r.reaction_key = fer.reaction_key
            JOIN warehouse.fact_drug_safety_events f ON f.event_id = fer.event_id
            JOIN warehouse.dim_drug d2 ON d2.drug_key = f.drug_key
            WHERE r.reaction_name = %s AND d2.drug_name <> %s
            GROUP BY d2.drug_name
            ORDER BY count DESC
            LIMIT 10
            """,
            (reaction_name, drug_name),
        )

        rationale = list(risk["rationale"])
        rationale.insert(
            0, f"Priority score {score:.2f}; serious rate {sr*100:.1f}%"
        )

        return {
            "drug": row["drug"],
            "reaction": row["reaction"],
            "risk_level": risk["risk_level"],
            "priority_score": score,
            "reports": total,
            "serious_reports": serious,
            "serious_rate": sr,
            "reporting_trend": trend,
            "associated_reactions": associated_reactions,
            "associated_drugs": associated_drugs,
            "data_quality": self._data_quality_status(),
            "rationale": rationale,
        }

    # ------------------------------------------------------------------
    # Data quality
    # ------------------------------------------------------------------

    def _data_quality_status(self) -> dict[str, Any]:
        try:
            nulls = self._query_one(
                """
                SELECT
                  COUNT(*) FILTER (WHERE event_id IS NULL)   AS event_id_nulls,
                  COUNT(*) FILTER (WHERE drug_key IS NULL)   AS drug_key_nulls,
                  COUNT(*) FILTER (WHERE date_key IS NULL)   AS date_key_nulls,
                  COUNT(*) FILTER (WHERE serious IS NULL)    AS serious_nulls
                FROM warehouse.fact_drug_safety_events
                """
            )
            dup = self._query_one(
                """
                SELECT COUNT(*) AS dup_count FROM (
                  SELECT event_id FROM warehouse.fact_drug_safety_events
                  GROUP BY event_id HAVING COUNT(*) > 1
                ) t
                """
            )
            nulls = nulls or {}
            dup_count = int(dup["dup_count"]) if dup else 0
            dq = {
                "required_fields_validated": all(
                    int(nulls.get(k, 0)) == 0
                    for k in [
                        "event_id_nulls",
                        "drug_key_nulls",
                        "date_key_nulls",
                        "serious_nulls",
                    ]
                ),
                "null_counts": {k: int(v) for k, v in nulls.items()},
                "duplicate_events": dup_count,
                "duplicate_checks_passed": dup_count == 0,
                "status": "PASS" if dup_count == 0 else "WARNING",
            }
            return dq
        except Exception:
            return {"status": "UNKNOWN", "note": "Data quality check unavailable"}


_database_service: Optional[DatabaseService] = None


def get_database_service() -> DatabaseService:
    """Return a shared DatabaseService instance."""
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
    return _database_service
