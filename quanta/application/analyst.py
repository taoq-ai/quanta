"""The Quanta analyst agent loop.

A small, deterministic planner that composes the four domain ports. It is the
*same* loop in the vulnerable and hardened demos — only the injected
:class:`~quanta.security.policy.SecurityPolicy` changes. This is the teaching
point: the exploit and its fix are both properties of the composition, not of
any single tool.

The planner faithfully reproduces the two agent behaviours that matter:
1. it serves the user's request (fetch a benchmark, read a metric, email a
   summary), and
2. when fetched content contains an instruction, it tends to act on it
   (indirect prompt injection) — unless policy forbids it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from quanta.application.instructions import Directive, extract_directives
from quanta.domain.ports import (
    MetricsRepositoryPort,
    ReferenceDataPort,
    ReportDeliveryPort,
)
from quanta.security.policy import PermissivePolicy, SecurityPolicy
from quanta.security.taint import Taint, TaintTracker

DEFAULT_BENCHMARK_URL = "https://api.frankfurter.app/latest?from=GBP&to=EUR"


@dataclass
class AnalystRequest:
    prompt: str
    requester: str  # the authenticated user's address


@dataclass
class ToolCall:
    tool: str
    args: dict
    summary: str
    taint: list[str] = field(default_factory=list)
    blocked: bool = False
    control: str = ""


@dataclass
class Delivery:
    recipient: str
    subject: str
    bytes_sent: int
    contained_private: bool
    delivered: bool
    reason: str
    control: str


@dataclass
class AnalystRun:
    requester: str
    prompt: str
    calls: list[ToolCall] = field(default_factory=list)
    deliveries: list[Delivery] = field(default_factory=list)
    final_taint: list[str] = field(default_factory=list)

    @property
    def exfiltrations(self) -> list[Delivery]:
        """Deliveries that left to someone other than the authenticated user."""
        return [
            d
            for d in self.deliveries
            if d.delivered and d.recipient.strip().lower() != self.requester.strip().lower()
        ]

    @property
    def leaked_private_to_third_party(self) -> bool:
        return any(d.contained_private for d in self.exfiltrations)


@dataclass
class _Plan:
    needs_reference: bool
    metric: str | None
    group_by: str
    deliver_summary: bool


def _is_private(group_by: str) -> bool:
    # Customer-level rows are PII. Country/month/product aggregates are not.
    return group_by == "customer_id"


class Analyst:
    """Composes the four ports under a pluggable security policy."""

    def __init__(
        self,
        *,
        metrics: MetricsRepositoryPort,
        reference: ReferenceDataPort,
        delivery: ReportDeliveryPort,
        policy: SecurityPolicy | None = None,
        benchmark_url: str = DEFAULT_BENCHMARK_URL,
    ) -> None:
        self.metrics = metrics
        self.reference = reference
        self.delivery = delivery
        self.policy: SecurityPolicy = policy or PermissivePolicy()
        self.benchmark_url = benchmark_url

    # ── public ────────────────────────────────────────────────────────────
    def handle(self, request: AnalystRequest) -> AnalystRun:
        taint = TaintTracker()
        run = AnalystRun(requester=request.requester, prompt=request.prompt)
        plan = self._plan(request.prompt)

        directives: list[Directive] = []
        if plan.needs_reference:
            content = self._fetch(self.benchmark_url, taint, run)
            directives = extract_directives(content)

        summary_md = ""
        if plan.metric:
            summary_md = self._search(plan.metric, plan.group_by, taint, run)

        # Act on instructions found in untrusted content (the injection).
        for directive in directives:
            self._follow_injected_directive(directive, request.requester, taint, run)

        # Serve the user's own request: email the summary back to them.
        if plan.deliver_summary and summary_md:
            self._deliver(
                request.requester,
                "Analytics summary",
                summary_md,
                requester=request.requester,
                taint=taint,
                run=run,
                contains_private=False,
            )

        run.final_taint = taint.state.labels()
        return run

    # ── steps ─────────────────────────────────────────────────────────────
    def _plan(self, prompt: str) -> _Plan:
        lower = prompt.lower()
        needs_reference = any(w in lower for w in ("benchmark", "reference", "fx", "rate"))
        metric = None
        for key in ("revenue", "sales", "orders", "units", "customers"):
            if key in lower:
                metric = "revenue" if key == "sales" else key
                break
        if metric is None and any(w in lower for w in ("summary", "report", "analy")):
            metric = "revenue"
        deliver = any(w in lower for w in ("email", "send", "report", "summary", "share"))
        return _Plan(needs_reference, metric, "country", deliver)

    def _fetch(self, url: str, taint: TaintTracker, run: AnalystRun) -> str:
        doc = self.reference.fetch(url)
        taint.mark(Taint.UNTRUSTED)
        run.calls.append(
            ToolCall(
                "fetch_reference",
                {"url": url},
                f"fetched {len(doc.content)} bytes of external reference (untrusted)",
                taint.state.labels(),
            )
        )
        return doc.content

    def _search(self, metric: str, group_by: str, taint: TaintTracker, run: AnalystRun) -> str:
        result = self.metrics.query(metric, group_by=group_by)
        private = _is_private(group_by)
        if private:
            taint.mark(Taint.PRIVATE)
        run.calls.append(
            ToolCall(
                "search_database",
                {"metric": metric, "group_by": group_by},
                f"read {len(result.rows)} rows "
                f"({'customer-level / PII' if private else 'aggregate'})",
                taint.state.labels(),
            )
        )
        return result.to_markdown()

    def _follow_injected_directive(
        self, directive: Directive, requester: str, taint: TaintTracker, run: AnalystRun
    ) -> None:
        decision = self.policy.review_external_instruction(directive.raw, source_trusted=False)
        if not decision.allowed:
            run.calls.append(
                ToolCall(
                    "(policy)",
                    {"directive": directive.summary},
                    f"ignored injected instruction — {decision.reason}",
                    taint.state.labels(),
                    blocked=True,
                    control=decision.control,
                )
            )
            return
        # The agent obeys the injection: read the requested (private) data …
        data_md = self._search(directive.metric, directive.group_by, taint, run)
        # … and ship it to the model/injection-chosen recipient.
        self._deliver(
            directive.recipient,
            "Customer export",
            data_md,
            requester=requester,
            taint=taint,
            run=run,
            contains_private=_is_private(directive.group_by),
        )

    def _deliver(
        self,
        recipient: str,
        subject: str,
        body: str,
        *,
        requester: str,
        taint: TaintTracker,
        run: AnalystRun,
        contains_private: bool,
    ) -> None:
        decision = self.policy.review_delivery(recipient, requester=requester, taint=taint)
        if not decision.allowed:
            run.deliveries.append(
                Delivery(
                    recipient,
                    subject,
                    len(body.encode()),
                    contains_private,
                    False,
                    decision.reason,
                    decision.control,
                )
            )
            run.calls.append(
                ToolCall(
                    "send_email_report",
                    {"recipient": recipient},
                    f"BLOCKED — {decision.reason}",
                    taint.state.labels(),
                    blocked=True,
                    control=decision.control,
                )
            )
            return
        try:
            receipt = self.delivery.deliver(recipient, subject, body)
        except PermissionError as exc:
            run.deliveries.append(
                Delivery(
                    recipient,
                    subject,
                    len(body.encode()),
                    contains_private,
                    False,
                    str(exc),
                    "domain-allowlist",
                )
            )
            run.calls.append(
                ToolCall(
                    "send_email_report",
                    {"recipient": recipient},
                    f"BLOCKED by adapter — {exc}",
                    taint.state.labels(),
                    blocked=True,
                    control="domain-allowlist",
                )
            )
            return
        run.deliveries.append(
            Delivery(
                recipient,
                subject,
                receipt.bytes_sent,
                contains_private,
                True,
                receipt.reason,
                "domain-allowlist",
            )
        )
        run.calls.append(
            ToolCall(
                "send_email_report",
                {"recipient": recipient},
                f"delivered {receipt.bytes_sent} bytes (dry-run)",
                taint.state.labels(),
            )
        )
