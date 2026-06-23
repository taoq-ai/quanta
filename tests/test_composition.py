"""The point of the whole repo: ZIRAN flags the tool *composition*.

Every tool passes its own tests (test_tools.py). This test proves that the
combination — search_database -> send_email_report — is still a critical data
exfiltration path, found by ZIRAN's built-in patterns, not by us labelling it.

Skipped automatically if ZIRAN is not installed.
"""

from __future__ import annotations

import pytest

ziran = pytest.importorskip("ziran", reason="install dev extras (ziran) to run composition test")

from ziran.application.knowledge_graph.chain_analyzer import ToolChainAnalyzer  # noqa: E402
from ziran.application.knowledge_graph.graph import AttackKnowledgeGraph, EdgeType  # noqa: E402
from ziran.domain.entities.capability import AgentCapability, CapabilityType  # noqa: E402

from quanta.capabilities import DATA_FLOW, TOOL_CATALOG  # noqa: E402


def _build_graph() -> AttackKnowledgeGraph:
    graph = AttackKnowledgeGraph()
    for spec in TOOL_CATALOG:
        graph.add_capability(
            spec.id,
            AgentCapability(
                id=spec.id,
                name=spec.name,
                type=CapabilityType.TOOL,
                description=spec.description,
                dangerous=False,  # individually approved
            ),
        )
    for src, tgt in DATA_FLOW:
        graph.add_edge(src, tgt, EdgeType.CAN_CHAIN_TO, {})
    return graph


def test_exfiltration_composition_is_detected() -> None:
    chains = ToolChainAnalyzer(_build_graph()).analyze()
    exfil = [c for c in chains if c.vulnerability_type == "data_exfiltration"]
    assert exfil, "ZIRAN did not flag the exfiltration composition"

    headline = next(c for c in exfil if c.risk_level == "critical")
    assert headline.graph_path[0] == "search_database"
    assert headline.graph_path[-1] == "send_email_report"


def test_individual_tools_are_not_flagged_alone() -> None:
    # A graph with the tools but NO composition edges yields no dangerous chains.
    graph = AttackKnowledgeGraph()
    for spec in TOOL_CATALOG:
        graph.add_capability(
            spec.id,
            AgentCapability(id=spec.id, name=spec.name, type=CapabilityType.TOOL, dangerous=False),
        )
    assert ToolChainAnalyzer(graph).analyze() == []
