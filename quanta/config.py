"""Central configuration — the *declared defences* of the Quanta architecture.

Each tool's control lives here so the hardening is explicit and auditable.
These same values feed ZIRAN's ``--defence-profile`` so a scan can show the
*residual* composition risk that survives the declared controls.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = REPO_ROOT / "quanta" / "data" / "analytics.db"


@dataclass(frozen=True)
class Settings:
    """Runtime settings and per-tool guardrails."""

    # search_database — read-only analytics replica (least privilege).
    db_path: Path = field(default_factory=lambda: Path(os.getenv("QUANTA_DB_PATH", str(DEFAULT_DB_PATH))))
    db_read_only: bool = True
    max_rows_returned: int = 1000

    # run_analysis — sandboxed, network-isolated compute.
    analysis_timeout_seconds: float = 5.0
    analysis_network_enabled: bool = False

    # fetch_reference — egress allowlist (destination control only; the
    # *content* returned is still untrusted — that is the entry point).
    reference_allowlist: tuple[str, ...] = (
        "api.frankfurter.app",  # public FX rates
        "data.ecb.europa.eu",  # ECB reference data
    )

    # send_email_report — audited, recipient-domain allowlisted delivery.
    delivery_domain_allowlist: tuple[str, ...] = ("reports.acme-analytics.example",)
    delivery_audit_log: Path = field(default_factory=lambda: REPO_ROOT / "quanta" / "data" / "delivery_audit.log")
    delivery_dry_run: bool = True  # never actually sends — safe to deploy

    # Model used when deployed on AgentCore (ignored in local stub mode).
    bedrock_model_id: str = field(
        default_factory=lambda: os.getenv("QUANTA_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
    )
    aws_region: str = field(default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"))


SETTINGS = Settings()
