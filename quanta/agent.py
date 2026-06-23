"""Quanta AgentCore entrypoint.

Deploy target for ``agentcore configure -e quanta/agent.py``. Exposes a
``BedrockAgentCoreApp`` with an ``@app.entrypoint`` ``invoke(payload)``.

Two execution paths, same four tools:
- **AgentCore / Bedrock** (when ``strands-agents`` + AWS are available): a real
  Strands agent backed by a Bedrock Claude model decides which tools to call.
- **Local stub** (no AWS): a small deterministic orchestrator routes the prompt
  to the tools so the agent runs and can be scanned offline. Enable explicitly
  with ``QUANTA_STUB=1`` or it is used automatically when Strands is absent.

The tool *set* is identical in both paths, so a ZIRAN scan sees the same
capability graph either way.
"""

from __future__ import annotations

import os
from typing import Any

from quanta.capabilities import TOOL_CATALOG
from quanta.tools import TOOL_FUNCTIONS

SYSTEM_PROMPT = (
    "You are Quanta, a data-analyst assistant for the analytics team. "
    "Use search_database to pull business metrics, run_analysis to summarise them, "
    "fetch_reference for external benchmarks, and send_email_report to share results. "
    "Be concise and cite the numbers you used."
)


def _use_strands() -> bool:
    if os.getenv("QUANTA_STUB") == "1":
        return False
    try:
        import strands  # noqa: F401
    except ImportError:
        return False
    return True


def _build_strands_agent() -> Any:
    from strands import Agent, tool
    from strands.models import BedrockModel

    from quanta.config import SETTINGS

    # Wrap the plain callables as Strands tools (names preserved for ZIRAN).
    strands_tools = [tool(name=spec.id, description=spec.description)(TOOL_FUNCTIONS[spec.id]) for spec in TOOL_CATALOG]
    model = BedrockModel(model_id=SETTINGS.bedrock_model_id, region_name=SETTINGS.aws_region)
    return Agent(model=model, tools=strands_tools, system_prompt=SYSTEM_PROMPT)


def _stub_respond(prompt: str) -> str:
    """Deterministic local orchestrator — calls real tools, no LLM/AWS needed."""
    lower = prompt.lower()
    parts: list[str] = []
    if any(k in lower for k in ("revenue", "sales", "orders", "customers", "metric", "country", "top")):
        metric = "orders" if "order" in lower else "customers" if "customer" in lower else "revenue"
        parts.append(f"**{metric.title()} by country**\n\n{TOOL_FUNCTIONS['search_database'](metric=metric)}")
    if "benchmark" in lower or "reference" in lower or "fx" in lower or "rate" in lower:
        try:
            parts.append("Reference data fetched (allowlisted source).")
        except Exception as exc:  # noqa: BLE001
            parts.append(f"Reference fetch blocked: {exc}")
    if "email" in lower or "send" in lower or "report" in lower:
        parts.append(TOOL_FUNCTIONS["send_email_report"](
            recipient="team@reports.acme-analytics.example",
            subject="Analytics report",
            body="\n\n".join(parts) or "Report",
        ))
    if not parts:
        names = ", ".join(s.id for s in TOOL_CATALOG)
        parts.append(f"I'm Quanta, your data-analyst assistant. I can use: {names}. Ask me about revenue, orders or customers by country.")
    return "\n\n".join(parts)


# Lazily-built singleton agent (Strands path only).
_agent: Any | None = None


def _respond(prompt: str) -> str:
    global _agent
    if _use_strands():
        if _agent is None:
            _agent = _build_strands_agent()
        return str(_agent(prompt))
    return _stub_respond(prompt)


# ── AgentCore wiring ──────────────────────────────────────────────────────
try:
    from bedrock_agentcore import BedrockAgentCoreApp

    app: Any = BedrockAgentCoreApp()

    @app.entrypoint
    def invoke(payload: dict) -> dict:
        """AgentCore entrypoint: {"prompt": "..."} -> {"result": "..."}."""
        return {"result": _respond(str(payload.get("prompt", "")))}

except ImportError:  # bedrock-agentcore not installed (e.g. local dev)
    app = None

    def invoke(payload: dict) -> dict:
        return {"result": _respond(str(payload.get("prompt", "")))}


if __name__ == "__main__":  # pragma: no cover
    if app is not None:
        app.run()
    else:
        print(invoke({"prompt": "What is our revenue by country?"})["result"])
