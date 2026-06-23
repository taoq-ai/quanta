"""Minimal taint tracking for an agent run.

Two labels matter for the lethal trifecta:

- ``PRIVATE``   — data read from an internal source (``search_database``).
- ``UNTRUSTED`` — content ingested from outside (``fetch_reference``), which may
  carry an indirect prompt injection.

A run that has accumulated both labels and then reaches an external sink
(``send_email_report``) is the exfiltration path. The tracker lets the hardened
policy reason about *what the agent is currently holding*, which no per-tool
control can see.
"""

from __future__ import annotations

from enum import Flag, auto


class Taint(Flag):
    NONE = 0
    PRIVATE = auto()
    UNTRUSTED = auto()

    def labels(self) -> list[str]:
        return [str(t.name) for t in (Taint.PRIVATE, Taint.UNTRUSTED) if t in self]


class TaintTracker:
    """Accumulates taint labels over the course of a single agent run."""

    def __init__(self) -> None:
        self._state = Taint.NONE

    @property
    def state(self) -> Taint:
        return self._state

    def mark(self, taint: Taint) -> None:
        self._state |= taint

    def has(self, taint: Taint) -> bool:
        return taint in self._state

    def holds_trifecta(self) -> bool:
        """True once the run holds both private data and untrusted content."""
        return self.has(Taint.PRIVATE) and self.has(Taint.UNTRUSTED)
