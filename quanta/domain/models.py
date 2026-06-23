"""Domain value objects passed across ports."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class QueryResult:
    """Result of a metrics query against the read-only replica."""

    columns: list[str]
    rows: list[tuple]
    truncated: bool = False

    def to_markdown(self) -> str:
        head = "| " + " | ".join(self.columns) + " |"
        sep = "| " + " | ".join("---" for _ in self.columns) + " |"
        body = "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in self.rows)
        note = "\n_(results truncated)_" if self.truncated else ""
        return f"{head}\n{sep}\n{body}{note}"


@dataclass(frozen=True)
class ReferenceDocument:
    """External reference content. NOTE: ``content`` is UNTRUSTED input."""

    url: str
    content: str
    trusted: bool = False  # never True — this is the untrusted-content boundary


@dataclass(frozen=True)
class DeliveryReceipt:
    """Audit record of a report delivery attempt."""

    recipient: str
    bytes_sent: int
    allowed: bool
    dry_run: bool
    reason: str = ""
    metadata: dict = field(default_factory=dict)
