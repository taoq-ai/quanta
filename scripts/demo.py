#!/usr/bin/env python3
"""Quanta live-demo driver — the single entry point for the talk demo.

All Python, no shell. From the repo root:

    python scripts/demo.py                 # the whole demo: ask -> scan -> exploit
    python scripts/demo.py --pause         # wait for <enter> between steps (on stage)

    python scripts/demo.py ask             # 3 analytics questions (offline stub)
    python scripts/demo.py ask --cloud "revenue by country, top 5"   # deployed agent
    python scripts/demo.py scan            # run ZIRAN + open the report (installs ZIRAN if missing)
    python scripts/demo.py exploit         # the breach, then the hardened fix
    python scripts/demo.py deploy          # agentcore configure + launch

The offline parts (ask, exploit) need nothing installed. `scan` needs ZIRAN and
will install it for you (use --no-install to fall back to the frozen report).
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

QUESTIONS = [
    "What was our revenue by country? Give me the top 5.",
    "How many orders did we get per country?",
    "Who are our top customers by number of orders?",
]

PAUSE = False


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _step(msg: str) -> None:
    print("\n" + _c("1;36", f"== {msg}"))


def _cmd(msg: str) -> None:
    print(_c("2", f"$ {msg}"))


def _pause() -> None:
    if PAUSE:
        with contextlib.suppress(EOFError):
            input(_c("2", "   …press enter… "))


def _child_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def _ziran_installed() -> bool:
    try:
        import ziran  # noqa: F401
    except ModuleNotFoundError:
        return False
    return True


def _install_ziran() -> None:
    local = ROOT.parent / "ziran"
    if (local / "pyproject.toml").exists():
        args = [sys.executable, "-m", "pip", "install", "-e", str(local)]
        _cmd(f"pip install -e {local}")
    else:
        args = [sys.executable, "-m", "pip", "install", "ziran[agentcore]"]
        _cmd("pip install 'ziran[agentcore]'")
    print(_c("2", "   installing ZIRAN…"))
    subprocess.run(args, check=False)


# ── steps ────────────────────────────────────────────────────────────────────
def do_ask(questions: list[str], cloud: bool) -> None:
    _step("Quanta is a real analytics assistant")
    if cloud:
        for q in questions:
            _cmd(f"agentcore invoke '{json.dumps({'prompt': q})}'")
            subprocess.run(["agentcore", "invoke", json.dumps({"prompt": q})], check=False)
            _pause()
        return
    os.environ["QUANTA_STUB"] = "1"
    sys.path.insert(0, str(ROOT))
    from quanta.agent import invoke

    for q in questions:
        _cmd(f'quanta agent (offline stub) ← "{q}"')
        print(f"\n>>> {q}\n")
        print(invoke({"prompt": q})["result"])
        _pause()


def do_scan(out: Path, no_install: bool) -> None:
    _step("Now turn ZIRAN on it — find what the tools can do *together*")
    if not _ziran_installed() and not no_install:
        _install_ziran()

    out.mkdir(parents=True, exist_ok=True)
    html: Path | None = None
    if _ziran_installed():
        script = ROOT / "scripts" / "scan_quanta.py"
        _cmd(f"python scripts/{script.name} --out {out}")
        env = _child_env()
        env["QUANTA_STUB"] = "1"
        subprocess.run([sys.executable, str(script), "--out", str(out)], check=True, env=env)
        reports = sorted(out.glob("*_report.html"), key=lambda p: p.stat().st_mtime, reverse=True)
        html = reports[0] if reports else None
    else:
        print(_c("33", "   ZIRAN unavailable — opening the pre-generated report instead."))
        html = ROOT / "reports" / "quanta_scan_report.html"

    if html and html.exists():
        _cmd(f"open {html}")
        webbrowser.open(html.resolve().as_uri())
    _pause()


def do_exploit() -> None:
    _step("Watch the composition get exploited, then blocked")
    script = ROOT / "scripts" / "exploit_demo.py"
    _cmd("python scripts/exploit_demo.py")
    subprocess.run([sys.executable, str(script)], check=True, env=_child_env())


def do_deploy() -> None:
    _step("Deploy Quanta to Amazon Bedrock AgentCore Runtime")
    region = os.environ.setdefault("AWS_REGION", "us-east-1")
    if shutil.which("agentcore") is None:
        _cmd("pip install bedrock-agentcore-starter-toolkit")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "bedrock-agentcore-starter-toolkit"],
            check=True,
        )
    _cmd("python -m quanta.data_loader   # build the read-only analytics replica")
    subprocess.run([sys.executable, "-m", "quanta.data_loader"], check=False, env=_child_env())

    configure = [
        "agentcore",
        "configure",
        "--entrypoint",
        "quanta/agent.py",
        "--name",
        "quanta",
        "--region",
        region,
        "--requirements-file",
        "requirements.txt",
        "--non-interactive",
    ]
    role = os.environ.get("AGENTCORE_EXECUTION_ROLE_ARN")
    if role:
        configure += ["--execution-role", role]
    _cmd(" ".join(configure))
    subprocess.run(configure, check=True)

    _cmd("agentcore launch --auto-update-on-conflict")
    subprocess.run(["agentcore", "launch", "--auto-update-on-conflict"], check=True)
    subprocess.run(["agentcore", "status"], check=False)
    print("\nDone. Try:  python scripts/demo.py ask --cloud")


# ── cli ──────────────────────────────────────────────────────────────────────
def main() -> None:
    global PAUSE
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--pause", action="store_true", help="wait for <enter> between steps")
    sub = parser.add_subparsers(dest="cmd")

    pa = sub.add_parser("ask", help="run the analytics questions")
    pa.add_argument("questions", nargs="*")
    pa.add_argument("--cloud", action="store_true", help="use the deployed AgentCore agent")

    ps = sub.add_parser("scan", help="run ZIRAN and open the report")
    ps.add_argument("--out", type=Path, default=ROOT / "reports")
    ps.add_argument("--no-install", action="store_true", help="don't auto-install ZIRAN")

    sub.add_parser("exploit", help="run the breach + hardened fix")
    sub.add_parser("deploy", help="deploy to Amazon Bedrock AgentCore")
    pall = sub.add_parser("all", help="ask -> scan -> exploit (default)")
    pall.add_argument("--cloud", action="store_true")
    pall.add_argument("--no-install", action="store_true")

    args = parser.parse_args()
    PAUSE = args.pause

    cmd = args.cmd or "all"
    if cmd == "ask":
        do_ask(args.questions or QUESTIONS, args.cloud)
    elif cmd == "scan":
        do_scan(args.out, args.no_install)
    elif cmd == "exploit":
        do_exploit()
    elif cmd == "deploy":
        do_deploy()
    else:  # all
        do_ask(QUESTIONS, getattr(args, "cloud", False))
        do_scan(ROOT / "reports", getattr(args, "no_install", False))
        do_exploit()


if __name__ == "__main__":
    main()
