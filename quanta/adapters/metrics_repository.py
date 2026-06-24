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

# Allowlisted metric definitions — (aggregate expression, output alias). The
# model picks a key, never writes SQL.
_METRICS: dict[str, tuple[str, str]] = {
    "revenue": ("ROUND(SUM(quantity * price), 2)", "revenue"),
    "orders": ("COUNT(DISTINCT invoice_no)", "orders"),
    "units": ("SUM(quantity)", "units"),
    "customers": ("COUNT(DISTINCT customer_id)", "customers"),
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

    def _run(self, sql: str, params: tuple) -> tuple[list[str], list[tuple]]:
        with self._connect() as conn:
            cur = conn.execute(sql, params)
            return [d[0] for d in cur.description], cur.fetchall()

    def query(
        self, metric: str, *, group_by: str | None = None, limit: int | None = None
    ) -> QueryResult:
        if metric not in _METRICS:
            raise ValueError(f"unknown metric {metric!r}; choose from {sorted(_METRICS)}")
        agg, alias = _METRICS[metric]
        requested = (group_by or "country").strip().lower()
        requested = _GROUP_ALIASES.get(requested, requested)
        group = requested if requested in _GROUP_COLUMNS else "country"
        cap = min(limit or SETTINGS.max_rows_returned, SETTINGS.max_rows_returned)

        if group == "customer_id":
            # Join the customers dimension so results are meaningful (name +
            # email) — and so the customer-level export is real PII, not bare
            # IDs. Fall back to bare IDs on older DBs without a customers table.
            join_sql = (
                f"SELECT c.name, c.email, {agg} AS {alias} "
                "FROM invoices i JOIN customers c ON c.customer_id = i.customer_id "
                f"GROUP BY i.customer_id ORDER BY {alias} DESC LIMIT ?"
            )
            try:
                cols, rows = self._run(join_sql, (cap + 1,))
            except sqlite3.OperationalError:
                cols, rows = self._run(
                    f"SELECT customer_id, {agg} AS {alias} FROM invoices "
                    f"GROUP BY customer_id ORDER BY {alias} DESC LIMIT ?",
                    (cap + 1,),
                )
        else:
            cols, rows = self._run(
                f"SELECT {group}, {agg} AS {alias} FROM invoices "
                f"GROUP BY {group} ORDER BY {alias} DESC LIMIT ?",
                (cap + 1,),
            )
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
