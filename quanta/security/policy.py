"""Security policies — the difference between the vulnerable and hardened agent.

The agent loop (``quanta.application.analyst.Analyst``) is identical in both
cases. Only the injected :class:`SecurityPolicy` changes. That is the whole
point: the fix is not new tools or better prompts, it is a design-time policy
over the *composition*.

``PermissivePolicy`` models the everyday agent: it trusts tool output, follows
instructions it finds in fetched content, and lets the model choose recipients.
Every per-tool control still holds — and it is still exploitable.

``HardenedPolicy`` breaks the graph with three rules:
  1. **No instructions from data** — content from ``fetch_reference`` is data,
     never commands (kills indirect prompt injection, OWASP LLM01).
  2. **Recipient binding** — ``send_email_report`` may only target the
     authenticated requester, not a model/injection-chosen address
     (kills excessive agency / confused deputy, OWASP LLM06/LLM08).
  3. **Trifecta gate** — a run holding both private data and untrusted content
     may not reach an external sink at all without human review.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from quanta.security.taint import TaintTracker


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    control: str = ""  # which control made the call (for teaching/output)

    def __bool__(self) -> bool:  # convenience
        return self.allowed


@runtime_checkable
class SecurityPolicy(Protocol):
    def review_external_instruction(self, directive: str, *, source_trusted: bool) -> Decision:
        """Should an instruction found in tool output be obeyed?"""
        ...

    def review_delivery(self, recipient: str, *, requester: str, taint: TaintTracker) -> Decision:
        """Should an outbound report to ``recipient`` be allowed?"""
        ...


class PermissivePolicy:
    """The everyday agent. Default-allow. Each per-tool control still applies."""

    name = "permissive (default-allow)"

    def review_external_instruction(self, directive: str, *, source_trusted: bool) -> Decision:
        # Treats fetched content as if it were a trusted instruction — exactly
        # how a naive LLM agent behaves.
        return Decision(True, "model follows instructions found in tool output", "none")

    def review_delivery(self, recipient: str, *, requester: str, taint: TaintTracker) -> Decision:
        # Only the per-tool domain allowlist (enforced in the delivery adapter)
        # stands between the model and the outside world.
        return Decision(True, "recipient permitted (domain allowlist enforced downstream)", "none")


class HardenedPolicy:
    """Design-time controls over the composition. Breaks the exfiltration graph."""

    name = "hardened (taint + recipient-binding + trifecta-gate)"

    def review_external_instruction(self, directive: str, *, source_trusted: bool) -> Decision:
        if not source_trusted:
            return Decision(
                False,
                "instruction originated in untrusted fetched content — ignored as data",
                "no-instructions-from-data (LLM01)",
            )
        return Decision(True, "instruction from a trusted origin", "no-instructions-from-data")

    def review_delivery(self, recipient: str, *, requester: str, taint: TaintTracker) -> Decision:
        # Rule 2: recipient binding.
        if recipient.strip().lower() != requester.strip().lower():
            return Decision(
                False,
                f"recipient {recipient!r} is not the authenticated requester {requester!r}",
                "recipient-binding (LLM06)",
            )
        # Rule 3: trifecta gate — even to the requester, do not let a run that
        # holds both private + untrusted data reach an external sink unattended.
        if taint.holds_trifecta():
            return Decision(
                False,
                f"run holds the lethal trifecta ({'+'.join(taint.state.labels())}); "
                "external send requires human review",
                "trifecta-gate",
            )
        return Decision(True, "recipient is the authenticated requester; taint within policy", "ok")
