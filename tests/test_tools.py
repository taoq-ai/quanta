"""Each tool is individually defensible — these tests prove the controls hold."""

from __future__ import annotations

import sqlite3

import pytest

from quanta.adapters import (
    AllowlistedReferenceData,
    AuditedReportDelivery,
    ReadOnlyMetricsRepository,
)
from quanta.tools import run_analysis, search_database, send_email_report


def test_search_database_returns_metrics() -> None:
    out = search_database(metric="revenue", group_by="country", limit=5)
    assert "revenue" in out
    assert "United Kingdom" in out


def test_search_database_rejects_unknown_metric() -> None:
    with pytest.raises(ValueError, match="unknown metric"):
        ReadOnlyMetricsRepository().query("drop_table")


def test_database_is_read_only(analytics_db) -> None:
    conn = sqlite3.connect(f"file:{analytics_db}?mode=ro", uri=True)
    with pytest.raises(sqlite3.OperationalError):
        conn.execute("DELETE FROM invoices")


def test_reference_fetch_blocks_non_allowlisted_host() -> None:
    with pytest.raises(PermissionError, match="not on the reference allowlist"):
        AllowlistedReferenceData().fetch("https://evil.example.com/payload")


def test_delivery_blocks_non_allowlisted_domain() -> None:
    with pytest.raises(PermissionError, match="not in allowlist"):
        AuditedReportDelivery().deliver("attacker@evil.example.com", "x", "y")


def test_delivery_allows_allowlisted_domain_in_dry_run() -> None:
    out = send_email_report(
        recipient="team@reports.acme-analytics.example",
        subject="Report",
        body="numbers",
    )
    assert "dry-run" in out


def test_analysis_sandbox_has_no_imports() -> None:
    # __import__ is not in the sandbox builtins, so this must fail gracefully.
    out = run_analysis("__import__('os').system('echo pwned')")
    assert "analysis error" in out
