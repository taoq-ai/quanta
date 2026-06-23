"""Reference-data fetcher with an egress allowlist.

Control enforced here: outbound requests are restricted to an allowlist of
reference hosts. This is a real, useful control — it stops the agent calling
arbitrary hosts. But note what it does NOT do: it does not make the *returned
content* trustworthy. An allowlisted host can still serve text that contains an
indirect prompt injection (or be a doc/dataset an attacker influenced). That is
the untrusted-content boundary the composition exploits.
"""

from __future__ import annotations

from urllib.parse import urlparse

import httpx

from quanta.config import SETTINGS
from quanta.domain.models import ReferenceDocument


class AllowlistedReferenceData:
    """Fetch reference content from allowlisted hosts only."""

    def __init__(self, allowlist: tuple[str, ...] | None = None) -> None:
        self._allowlist = allowlist or SETTINGS.reference_allowlist

    def fetch(self, url: str) -> ReferenceDocument:
        host = urlparse(url).hostname or ""
        if host not in self._allowlist:
            raise PermissionError(
                f"host {host!r} is not on the reference allowlist {self._allowlist}"
            )
        resp = httpx.get(url, timeout=10.0, follow_redirects=False)
        resp.raise_for_status()
        # trusted=False, always: destination was checked, content was not.
        return ReferenceDocument(url=url, content=resp.text[:10_000], trusted=False)
