"""Security layer — the design-time controls that break the composition.

These are *graph-level* defences, not per-tool guardrails. The per-tool controls
(read-only replica, sandbox, allowlists, audit) already live in the adapters and
already pass review; they do not stop the exfiltration path. The policies here do,
by tracking taint across tools, binding recipients to the authenticated requester,
and refusing to let one agent run hold the whole lethal trifecta.
"""

from quanta.security.policy import Decision, HardenedPolicy, PermissivePolicy, SecurityPolicy
from quanta.security.taint import Taint, TaintTracker

__all__ = [
    "Decision",
    "HardenedPolicy",
    "PermissivePolicy",
    "SecurityPolicy",
    "Taint",
    "TaintTracker",
]
