"""Record the real ZIRAN interactive graph (vis-network) as an animated GIF.

Loads the generated HTML report, lets the physics settle, then does a slow
focus-zoom onto the critical `search_database -> send_email_report` exfiltration
edge and back out — capturing frames and encoding them with Pillow.

The first frame is the settled full graph, so the GIF still reads well as a
static image (e.g. if the deck is exported to PDF).

    uv run --project /path/to/ziran python talk/record_graph_gif.py

Requires a generated report (run scripts/scan_quanta.py first).
"""

from __future__ import annotations

import io
import time
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "quanta_scan_report.html"
OUT = ROOT / "talk" / "assets" / "ziran_graph.gif"

CRITICAL_NODE = "send_email_report"  # the exfiltration sink — zoom target
W, H = 1200, 720


def _frame(page, clip) -> Image.Image:
    return Image.open(io.BytesIO(page.screenshot(clip=clip))).convert("RGB")


def main() -> None:
    if not REPORT.exists():
        raise SystemExit(f"missing report: {REPORT} — run scripts/scan_quanta.py first")

    frames: list[Image.Image] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        page.goto(REPORT.resolve().as_uri())
        page.wait_for_selector("#graph-canvas canvas", timeout=15000)

        # Let physics stabilise, then fit the whole graph.
        time.sleep(3.0)
        page.evaluate("() => { try { network.fit({animation:false}); } catch(e){} }")
        time.sleep(0.6)

        box = page.eval_on_selector(
            "#graph-canvas",
            "el => { const r = el.getBoundingClientRect();"
            " return {x:r.x, y:r.y, width:r.width, height:r.height}; }",
        )
        clip = {"x": box["x"], "y": box["y"], "width": box["width"], "height": box["height"]}

        # Zoom is driven through the UI (mouse wheel) so it does not depend on the
        # page's JS internals. vis-network zooms toward the cursor — park it over
        # the critical search_database -> send_email_report region (lower-centre).
        tx = box["x"] + box["width"] * 0.45
        ty = box["y"] + box["height"] * 0.60
        page.mouse.move(tx, ty)

        # 1) hold the settled full graph (good first frame)
        for _ in range(5):
            frames.append(_frame(page, clip))
            time.sleep(0.08)

        # 2) zoom IN toward the exfiltration edge
        for _ in range(12):
            page.mouse.wheel(0, -110)
            time.sleep(0.05)
            frames.append(_frame(page, clip))

        # 3) hold on the critical edge
        for _ in range(5):
            frames.append(_frame(page, clip))
            time.sleep(0.1)

        # 4) zoom back OUT to the full graph
        for _ in range(12):
            page.mouse.wheel(0, 110)
            time.sleep(0.05)
            frames.append(_frame(page, clip))

        browser.close()

    # Downscale for size, encode looping GIF.
    target_w = 900
    scaled = [
        f.resize((target_w, round(f.height * target_w / f.width)), Image.LANCZOS) for f in frames
    ]
    quantized = [im.quantize(colors=128, method=Image.MEDIANCUT) for im in scaled]
    quantized[0].save(
        OUT,
        save_all=True,
        append_images=quantized[1:],
        duration=110,
        loop=0,
        optimize=True,
        disposal=2,
    )
    kb = OUT.stat().st_size / 1024
    print(f"wrote {OUT.name}: {len(frames)} frames, {kb:.0f} KB")


if __name__ == "__main__":
    main()
