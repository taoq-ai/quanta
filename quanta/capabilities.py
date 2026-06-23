"""Canonical catalogue of Quanta's tools and their data-flow surface.

Single source of truth used by:
- the agent (tool registration), and
- the ZIRAN scan (capability discovery + the composition graph).

The ``data_flow`` edges describe how results can move between tools. An LLM
agent can sequence these tools freely; the edges below model the realistic
forward data-flow (sources -> compute -> sink) as a DAG, which is what ZIRAN
analyses for dangerous compositions.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolSpec:
    id: str
    name: str
    description: str
    control: str  # the declared, individually-defensible guardrail
    role: str  # source-private | source-untrusted | compute | sink-external


TOOL_CATALOG: tuple[ToolSpec, ...] = (
    ToolSpec(
        id="search_database",
        name="Search Database",
        description="Search the read-only analytics replica for business metrics (revenue, orders, customers) by country, month, product or customer.",
        control="Read-only replica + parameterised query builder (no raw SQL) + row cap.",
        role="source-private",
    ),
    ToolSpec(
        id="run_analysis",
        name="Run Analysis",
        description="Run a sandboxed, network-isolated computation over query results to aggregate or summarise them.",
        control="Restricted sandbox: no network, no filesystem, no imports, time-limited.",
        role="compute",
    ),
    ToolSpec(
        id="fetch_reference",
        name="Fetch Reference",
        description="Fetch reference data (FX rates, public benchmarks) from an allowlisted set of external sources.",
        control="Egress allowlist on destination host. (Returned content is untrusted.)",
        role="source-untrusted",
    ),
    ToolSpec(
        id="send_email_report",
        name="Send Email Report",
        description="Deliver a templated analysis report to a recipient on an allowlisted domain.",
        control="Recipient-domain allowlist + append-only audit log + dry-run by default.",
        role="sink-external",
    ),
)

# Realistic forward data-flow (a DAG: sources -> compute -> external sink).
# This is the agent's *composition surface* — what its tools can do together.
DATA_FLOW: tuple[tuple[str, str], ...] = (
    ("search_database", "run_analysis"),
    ("search_database", "send_email_report"),
    ("fetch_reference", "run_analysis"),
    ("fetch_reference", "send_email_report"),
    ("run_analysis", "send_email_report"),
)


def tool_ids() -> list[str]:
    return [t.id for t in TOOL_CATALOG]
