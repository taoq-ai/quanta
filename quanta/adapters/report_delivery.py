"""Audited report delivery with a recipient-domain allowlist.

Control enforced here: recipients must be on an allowlisted domain; every
attempt is written to an append-only audit log; delivery is dry-run by default
so the agent is safe to deploy. These are good controls. The residual risk is
not in the tool: an allowlisted domain can still reach the wrong human, and any
data the model places in ``body`` rides out through this legitimate channel.
This is the external-communication leg of the lethal trifecta.
"""

from __future__ import annotations

from urllib.parse import urlparse

from quanta.config import SETTINGS
from quanta.domain.models import DeliveryReceipt


class AuditedReportDelivery:
    """Deliver (or, by default, dry-run) a report to an allowlisted domain."""

    def __init__(
        self,
        domain_allowlist: tuple[str, ...] | None = None,
        *,
        dry_run: bool | None = None,
    ) -> None:
        self._allowlist = domain_allowlist or SETTINGS.delivery_domain_allowlist
        self._dry_run = SETTINGS.delivery_dry_run if dry_run is None else dry_run

    def deliver(self, recipient: str, subject: str, body: str) -> DeliveryReceipt:
        domain = (
            recipient.split("@")[-1] if "@" in recipient else urlparse(recipient).hostname or ""
        )
        allowed = domain in self._allowlist
        receipt = DeliveryReceipt(
            recipient=recipient,
            bytes_sent=len(body.encode()),
            allowed=allowed,
            dry_run=self._dry_run,
            reason="ok" if allowed else f"domain {domain!r} not in allowlist",
            metadata={"subject": subject},
        )
        self._audit(receipt)
        if not allowed:
            raise PermissionError(receipt.reason)
        # dry_run: we never actually transmit — capability shape only.
        return receipt

    def _audit(self, receipt: DeliveryReceipt) -> None:
        log = SETTINGS.delivery_audit_log
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as fh:
            fh.write(
                f"recipient={receipt.recipient} bytes={receipt.bytes_sent} "
                f"allowed={receipt.allowed} dry_run={receipt.dry_run} reason={receipt.reason}\n"
            )
