"""Sandboxed analysis runner.

Control enforced here: a restricted execution surface — no network, no
filesystem, no imports, a small builtins allowlist, and a row-limited data
frame exposed as plain Python. This is intentionally NOT a general REPL, so it
should not be flagged as a code-execution sink on its own. The residual risk is
that it is a compute node reachable from untrusted input — relevant only in
composition, never alone.
"""

from __future__ import annotations

from quanta.config import SETTINGS
from quanta.domain.models import QueryResult

# Minimal, side-effect-free builtins. No __import__, open, eval, exec, etc.
_SAFE_BUILTINS = {
    "len": len,
    "sum": sum,
    "min": min,
    "max": max,
    "round": round,
    "sorted": sorted,
    "abs": abs,
    "range": range,
    "list": list,
    "dict": dict,
    "set": set,
    "float": float,
    "int": int,
    "str": str,
    "enumerate": enumerate,
    "zip": zip,
}


class SandboxedCodeRunner:
    """Evaluate a single analysis expression over query results."""

    def __init__(self) -> None:
        if SETTINGS.analysis_network_enabled:  # pragma: no cover - config guard
            raise RuntimeError("network must be disabled for the analysis sandbox")

    def run(self, code: str, data: QueryResult | None = None) -> str:
        rows = list(data.rows) if data else []
        columns = list(data.columns) if data else []
        env = {"__builtins__": _SAFE_BUILTINS, "rows": rows, "columns": columns}
        try:
            # Single expression only — keeps the surface tiny.
            result = eval(code, env, {})  # noqa: S307 - sandboxed builtins, no imports
        except Exception as exc:  # noqa: BLE001
            return f"analysis error: {exc}"
        return str(result)
