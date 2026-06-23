"""Scan the real Quanta agent with ZIRAN and render the report.

This is both the live-demo driver and the frozen-fallback generator. It:

1. discovers Quanta's four (individually-hardened) tools,
2. runs a ZIRAN campaign against the agent in-process (offline-safe: the stub
   orchestrator answers without AWS),
3. enriches the knowledge graph with the agent's composition surface (the
   data-flow edges between tools), and
4. runs the ToolChainAnalyzer + saves JSON / Markdown / interactive HTML.

The headline finding — ``search_database -> send_email_report`` data
exfiltration — comes from ZIRAN's built-in patterns, not from us. Every tool is
individually defensible; the graph is where the risk lives.

Run (from the quanta repo, with ziran installed):
    QUANTA_STUB=1 PYTHONPATH=. python scripts/scan_quanta.py --out reports
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from ziran.application.agent_scanner.scanner import AgentScanner
from ziran.application.attacks.library import AttackLibrary
from ziran.application.knowledge_graph.chain_analyzer import ToolChainAnalyzer
from ziran.application.knowledge_graph.graph import EdgeType
from ziran.domain.entities.capability import AgentCapability, CapabilityType
from ziran.domain.entities.phase import ScanPhase
from ziran.infrastructure.adapters.agentcore_adapter import AgentCoreAdapter
from ziran.interfaces.cli.reports import ReportGenerator

from quanta.agent import invoke
from quanta.capabilities import DATA_FLOW, TOOL_CATALOG


class QuantaAdapter(AgentCoreAdapter):
    """AgentCore adapter that reports Quanta's declared tool catalogue."""

    async def discover_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                id=spec.id,
                name=spec.name,
                type=CapabilityType.TOOL,
                description=f"{spec.description} [control: {spec.control}]",
                dangerous=False,  # each tool passes review individually
            )
            for spec in TOOL_CATALOG
        ]


def _enrich_composition(graph) -> None:
    """Add the agent's composition surface (tool -> tool data-flow edges)."""
    for src, tgt in DATA_FLOW:
        graph.add_edge(
            src, tgt, EdgeType.CAN_CHAIN_TO, {"reason": "agent can sequence these tools"}
        )


async def main() -> None:
    ap = argparse.ArgumentParser(description="Scan Quanta with ZIRAN")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "reports")
    ap.add_argument(
        "--full",
        action="store_true",
        help="run the full adversarial campaign (default: focused discovery + composition).",
    )
    args = ap.parse_args()

    # Default to a focused discovery scan so the report centres on the
    # composition finding — the thing no prompt-by-prompt review would catch.
    # --full adds the adversarial prompt phases for a complete campaign.
    focused = [ScanPhase.RECONNAISSANCE, ScanPhase.CAPABILITY_MAPPING]
    full = [
        ScanPhase.RECONNAISSANCE,
        ScanPhase.CAPABILITY_MAPPING,
        ScanPhase.VULNERABILITY_DISCOVERY,
        ScanPhase.EXPLOITATION_SETUP,
        ScanPhase.EXECUTION,
    ]
    phases = full if args.full else focused

    adapter = QuantaAdapter(entrypoint=invoke)
    scanner = AgentScanner(adapter=adapter, attack_library=AttackLibrary())

    caps = await adapter.discover_capabilities()
    print(f"Discovered {len(caps)} tools (all individually approved):")
    for c in caps:
        print(f"  - {c.name}")

    result = await scanner.run_campaign(phases=phases, stop_on_critical=False)

    # Add the composition surface and re-run the chain analyzer over it.
    _enrich_composition(scanner.graph)
    chains = ToolChainAnalyzer(scanner.graph).analyze()
    result.dangerous_tool_chains = [c.model_dump(mode="json") for c in chains]
    result.critical_chain_count = len([c for c in chains if c.risk_level == "critical"])
    result.metadata["dangerous_chain_count"] = len(chains)

    print(f"\nDangerous compositions found by ZIRAN: {len(chains)}")
    for c in chains:
        print(f"  [{c.risk_level.upper()}] {' -> '.join(c.graph_path)} : {c.vulnerability_type}")

    args.out.mkdir(parents=True, exist_ok=True)
    report = ReportGenerator(output_dir=args.out)
    json_path = report.save_json(result)
    md_path = report.save_markdown(result)
    html_path = report.save_html(result, graph_state=scanner.graph.export_state())
    print(f"\nReports written to {args.out}/")
    print(f"  JSON:     {json_path.name}")
    print(f"  Markdown: {md_path.name}")
    print(f"  HTML:     {html_path.name}  <- open this in a browser")


if __name__ == "__main__":
    asyncio.run(main())
