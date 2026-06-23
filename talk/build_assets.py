"""Render SVG diagrams (and optionally HTML) to PNG for the slide deck.

Uses Playwright's bundled Chromium so no system cairo/inkscape is needed.

    uv run --project /path/to/ziran python talk/build_assets.py
"""

from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "talk" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

# (source svg, output png, css width, css height)
SVGS = [
    (ROOT / "docs" / "architecture.svg", "architecture.png", 1100, 660),
    (ROOT / "docs" / "architecture-overlay.svg", "architecture-overlay.png", 1100, 660),
    (ROOT / "docs" / "c4-container.svg", "c4-container.png", 1200, 770),
    (ASSETS / "graph-evolution.svg", "graph-evolution.png", 1200, 460),
    (ASSETS / "lethal-trifecta.svg", "lethal-trifecta.png", 1000, 620),
    (ASSETS / "review-blindness.svg", "review-blindness.png", 1100, 560),
    (ASSETS / "credibility.svg", "credibility.png", 1100, 560),
    (ASSETS / "exploit_vulnerable.svg", "exploit_vulnerable.png", 1287, 368),
    (ASSETS / "exploit_hardened.svg", "exploit_hardened.png", 1287, 343),
]

SCALE = 2  # 2x for crisp projection


def _dims(svg: Path, w: int, h: int) -> tuple[int, int]:
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg.read_text())
    if m:
        return int(float(m.group(1))), int(float(m.group(2)))
    return w, h


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for svg, out, w, h in SVGS:
            if not svg.exists():
                print(f"  skip (missing): {svg.name}")
                continue
            vw, vh = _dims(svg, w, h)
            page = browser.new_page(viewport={"width": vw, "height": vh}, device_scale_factor=SCALE)
            page.goto(svg.resolve().as_uri())
            page.screenshot(path=str(ASSETS / out))
            page.close()
            print(f"  rendered {out}  ({vw}x{vh} @{SCALE}x)")
        browser.close()


if __name__ == "__main__":
    main()
