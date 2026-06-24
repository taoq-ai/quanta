"""Record the real Ziran interactive graph (vis-network) as an animated GIF.

Keeps the whole graph in frame the entire time and tours the attack paths using
the report's own ``highlightPath`` — each dangerous path lights up red while the
rest dims — then resets. No disorienting zoom; the motion is the highlight.

The first frame is the full settled graph, so the GIF still reads as a static
image (e.g. if the deck is exported to PDF).

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

        # Settle physics, then frame the whole graph and pin it there.
        time.sleep(3.0)
        page.evaluate(
            "() => { try { network.setOptions({physics:false});"
            " network.fit({animation:false}); } catch(e){} }"
        )
        time.sleep(0.5)

        box = page.eval_on_selector(
            "#graph-canvas",
            "el => { const r = el.getBoundingClientRect();"
            " return {x:r.x, y:r.y, width:r.width, height:r.height}; }",
        )
        clip = {"x": box["x"], "y": box["y"], "width": box["width"], "height": box["height"]}

        # highlightPath(i) dims everything and reds the path, then zooms to it —
        # we immediately fit() back so the FULL graph stays visible with the path lit.
        def hold(n: int, delay: float = 0.12) -> None:
            for _ in range(n):
                frames.append(_frame(page, clip))
                time.sleep(delay)

        def show_path(i: int) -> None:
            page.evaluate(
                "(i) => { try { highlightPath(i); network.fit({animation:false}); } catch(e){} }", i
            )
            time.sleep(0.15)

        def reset() -> None:
            page.evaluate(
                "() => { try { resetHighlight(); network.fit({animation:false}); } catch(e){} }"
            )
            time.sleep(0.15)

        # 1) full graph (good first frame)
        reset()
        hold(7)

        # 2) tour each attack path (search_database, send_email_report, run_analysis, ...)
        for i in (0, 3, 1, 2):
            show_path(i)
            hold(6)

        # 3) back to the full graph and hold
        reset()
        hold(7)

        browser.close()

    # Downscale + encode a smooth looping GIF.
    target_w = 940
    scaled = [
        f.resize((target_w, round(f.height * target_w / f.width)), Image.LANCZOS) for f in frames
    ]
    quantized = [im.quantize(colors=160, method=Image.MEDIANCUT) for im in scaled]
    quantized[0].save(
        OUT,
        save_all=True,
        append_images=quantized[1:],
        duration=320,
        loop=0,
        optimize=True,
        disposal=2,
    )
    kb = OUT.stat().st_size / 1024
    print(f"wrote {OUT.name}: {len(frames)} frames, {kb:.0f} KB")


if __name__ == "__main__":
    main()
