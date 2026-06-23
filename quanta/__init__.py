"""Quanta — a data-analyst AI agent for Amazon Bedrock AgentCore.

⚠️  EDUCATIONAL / DELIBERATELY COMPOSABLE. See DISCLAIMER.md.

Quanta is a *defensibly architected* analytics assistant: every tool is
individually hardened (read-only data replica, sandboxed compute, egress
allowlist, audited delivery). It is the companion demo target for ZIRAN's
tool-composition analysis — the point being that a clean, review-passing
architecture can still hide a graph-level exfiltration path.
"""

from quanta.capabilities import TOOL_CATALOG

__all__ = ["TOOL_CATALOG", "__version__"]
__version__ = "0.1.0"
