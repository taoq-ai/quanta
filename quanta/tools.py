"""The four Quanta tools — plain callables wired to the hardened adapters.

Framework-agnostic on purpose: ``agent.py`` adapts these into Strands ``@tool``
functions when running on AgentCore, and the local orchestrator calls them
directly. Each callable is thin; the control lives in its adapter.
"""

from __future__ import annotations

from collections.abc import Callable

from quanta.adapters import (
    AllowlistedReferenceData,
    AuditedReportDelivery,
    ReadOnlyMetricsRepository,
    SandboxedCodeRunner,
)
from quanta.domain.models import QueryResult

_metrics = ReadOnlyMetricsRepository()
_runner = SandboxedCodeRunner()
_reference = AllowlistedReferenceData()
_delivery = AuditedReportDelivery()

# Small in-process cache so run_analysis / send_email_report can reference the
# most recent query (mirrors how a real agent threads tool results).
_last_query: dict[str, QueryResult] = {}


def search_database(metric: str = "revenue", group_by: str = "country", limit: int = 20) -> str:
    """Search the read-only analytics replica for a business metric."""
    result = _metrics.query(metric, group_by=group_by, limit=limit)
    _last_query["result"] = result
    return result.to_markdown()


def run_analysis(code: str) -> str:
    """Run a sandboxed computation over the most recent query result."""
    return _runner.run(code, _last_query.get("result"))


def fetch_reference(url: str) -> str:
    """Fetch reference data from an allowlisted external source (untrusted content)."""
    doc = _reference.fetch(url)
    return doc.content


def send_email_report(recipient: str, subject: str, body: str) -> str:
    """Deliver a report to a recipient on an allowlisted domain (dry-run by default)."""
    receipt = _delivery.deliver(recipient, subject, body)
    status = "queued (dry-run)" if receipt.dry_run else "sent"
    return f"Report {status} to {receipt.recipient} ({receipt.bytes_sent} bytes)."


TOOL_FUNCTIONS: dict[str, Callable[..., str]] = {
    "search_database": search_database,
    "run_analysis": run_analysis,
    "fetch_reference": fetch_reference,
    "send_email_report": send_email_report,
}
