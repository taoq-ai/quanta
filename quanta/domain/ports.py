"""Ports — the interfaces the agent's tools depend on.

Adapters (infrastructure) implement these; the agent/tools depend only on the
abstractions. Each port docstring names the control its adapter must enforce.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from quanta.domain.models import DeliveryReceipt, QueryResult, ReferenceDocument


@runtime_checkable
class MetricsRepositoryPort(Protocol):
    """Read-only access to the analytics replica.

    Control: least-privilege, read-only connection; parameterised query
    builder (no raw SQL from the model); row cap.
    """

    def query(self, metric: str, *, group_by: str | None = None, limit: int | None = None) -> QueryResult: ...

    def customer_history(self, customer_id: str) -> QueryResult: ...


@runtime_checkable
class CodeRunnerPort(Protocol):
    """Sandboxed computation over in-memory result sets.

    Control: resource/time limits; no network; no filesystem.
    """

    def run(self, code: str, data: QueryResult | None = None) -> str: ...


@runtime_checkable
class ReferenceDataPort(Protocol):
    """Fetch external reference data.

    Control: egress allowlist (destination only). The returned content is
    UNTRUSTED — this is the indirect-injection entry point.
    """

    def fetch(self, url: str) -> ReferenceDocument: ...


@runtime_checkable
class ReportDeliveryPort(Protocol):
    """Deliver a report to a recipient.

    Control: recipient-domain allowlist; audit log; dry-run by default.
    """

    def deliver(self, recipient: str, subject: str, body: str) -> DeliveryReceipt: ...
