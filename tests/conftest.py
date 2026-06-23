"""Shared fixtures — build a synthetic analytics replica and point tools at it."""

from __future__ import annotations

from pathlib import Path

import pytest

from quanta.data_loader import load_synthetic


@pytest.fixture(scope="session", autouse=True)
def analytics_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    db = tmp_path_factory.mktemp("data") / "analytics.db"
    load_synthetic(db, n=2000)

    # The tools module instantiates its metrics repository at import time; point
    # it at the fixture DB so tests never touch a real replica.
    import quanta.tools as tools
    from quanta.adapters import ReadOnlyMetricsRepository

    tools._metrics = ReadOnlyMetricsRepository(db)
    return db
