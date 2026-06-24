"""Read-only metrics repository over the analytics replica.

Control enforced here:
- read-only SQLite connection (``mode=ro``),
- a *parameterised query builder* — the model never supplies raw SQL,
- a hard row cap.

This is exactly what a careful team would ship. The residual risk is not a
bug in this tool: its legitimate analytics scope still includes customer-level
rows (IDs, per-customer purchase history, country) that must not leave.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from quanta.config import SETTINGS
from quanta.domain.models import QueryResult

# Allowlisted metric definitions — the model picks a key, never writes SQL.
_METRICS: dict[str, str] = {
    "revenue": "SELECT {group}, ROUND(SUM(quantity * price), 2) AS revenue FROM invoices",
    "orders": "SELECT {group}, COUNT(DISTINCT invoice_no) AS orders FROM invoices",
    "units": "SELECT {group}, SUM(quantity) AS units FROM invoices",
    "customers": "SELECT {group}, COUNT(DISTINCT customer_id) AS customers FROM invoices",
}
_GROUP_COLUMNS = {"country", "month", "product", "customer_id"}
# Natural-language aliases an LLM is likely to pass (it says "customer", the
# column is "customer_id"). Unmapped values still fall back to "country".
_GROUP_ALIASES = {
    "customer": "customer_id",
    "customers": "customer_id",
    "countries": "country",
    "products": "product",
    "months": "month",
}


class ReadOnlyMetricsRepository:
    """Parameterised, read-only access to the analytics replica."""

    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path or SETTINGS.db_path

    def _connect(self) -> sqlite3.Connection:
        # Self-heal: if the replica is missing (e.g. not baked into the deployed
        # image), build a small offline synthetic sample so the agent still works.
        if not self._db_path.exists():
            from quanta.data_loader import load_synthetic

            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            load_synthetic(self._db_path)
        # Read-only URI connection — writes are impossible even if attempted.
        uri = f"file:{self._db_path}?mode=ro"
        return sqlite3.connect(uri, uri=True)

    def query(
        self, metric: str, *, group_by: str | None = None, limit: int | None = None
    ) -> QueryResult:
        if metric not in _METRICS:
            raise ValueError(f"unknown metric {metric!r}; choose from {sorted(_METRICS)}")
        requested = (group_by or "country").strip().lower()
        requested = _GROUP_ALIASES.get(requested, requested)
        group = requested if requested in _GROUP_COLUMNS else "country"
        cap = min(limit or SETTINGS.max_rows_returned, SETTINGS.max_rows_returned)
        sql = _METRICS[metric].format(group=group) + f" GROUP BY {group} ORDER BY 2 DESC LIMIT ?"
        with self._connect() as conn:
            cur = conn.execute(sql, (cap + 1,))
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
        truncated = len(rows) > cap
        return QueryResult(columns=cols, rows=rows[:cap], truncated=truncated)

    def customer_history(self, customer_id: str) -> QueryResult:
        # Parameterised — no injection surface. Still returns customer-level PII
        # by design ("an analyst needs per-customer detail").
        sql = (
            "SELECT invoice_no, invoice_date, country, "
            "ROUND(SUM(quantity * price), 2) AS spend "
            "FROM invoices WHERE customer_id = ? "
            "GROUP BY invoice_no, invoice_date, country "
            "ORDER BY invoice_date LIMIT ?"
        )
        with self._connect() as conn:
            cur = conn.execute(sql, (customer_id, SETTINGS.max_rows_returned))
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
        return QueryResult(columns=cols, rows=rows)
