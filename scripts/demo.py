#!/usr/bin/env python3
"""Quanta live-demo driver — the single entry point for the talk demo.

All Python, no shell. From the repo root:

    python scripts/demo.py                 # the whole demo: ask -> scan -> exploit
    python scripts/demo.py --pause         # wait for <enter> between steps (on stage)

    python scripts/demo.py ask             # 3 analytics questions (offline stub)
    python scripts/demo.py ask --online    # real Bedrock, in-process (no deploy)
    python scripts/demo.py ask --cloud     # the deployed AgentCore agent
    python scripts/demo.py scan            # run Ziran + open the report (installs Ziran if missing)
    python scripts/demo.py exploit         # the breach, then the hardened fix
    python scripts/demo.py deploy          # agentcore configure + launch

Three ways to run the agent: offline stub (default, no deps/AWS), --online (real
Bedrock locally), --cloud (deployed runtime). The offline parts (stub ask,
exploit) need nothing installed; `scan` needs Ziran and installs it for you.
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


def _ziran_available() -> bool:
    # Probe in a FRESH interpreter, not this one: a `pip install` done earlier in
    # this same run is on disk but invisible to the already-running process. A
    # child of sys.executable reads site-packages fresh, so this is accurate
    # before *and* after a runtime install.
    return (
        subprocess.run([sys.executable, "-c", "import ziran"], capture_output=True).returncode == 0
    )


def _install_ziran() -> None:
    local = ROOT.parent / "ziran"
    if (local / "pyproject.toml").exists():
        args = [sys.executable, "-m", "pip", "install", "-e", str(local)]
        _cmd(f"pip install -e {local}")
    else:
        args = [sys.executable, "-m", "pip", "install", "ziran[agentcore]"]
        _cmd("pip install 'ziran[agentcore]'")
    print(_c("2", "   installing Ziran…"))
    subprocess.run(args, check=False)


# ── steps ────────────────────────────────────────────────────────────────────
def do_ask(questions: list[str], *, cloud: bool = False, online: bool = False) -> None:
    _step("Quanta is a real analytics assistant")
    if cloud:
        # The deployed AgentCore runtime (real Bedrock, in the cloud).
        for q in questions:
            _cmd(f"agentcore invoke '{json.dumps({'prompt': q})}'")
            subprocess.run(["agentcore", "invoke", json.dumps({"prompt": q})], check=False)
            _pause()
        return

    sys.path.insert(0, str(ROOT))
    if online:
        # Real Strands + Bedrock, in-process — no deploy. Needs the agentcore
        # extra and AWS credentials with Bedrock model access.
        os.environ.pop("QUANTA_STUB", None)
        try:
            import strands  # noqa: F401
        except ImportError:
            print(_c("33", "   --online needs the agentcore extra and AWS credentials:"))
            print("     pip install -e '.[agentcore]'")
            print("     aws sso login   (or export AWS_* keys)   ·   export AWS_REGION=eu-west-1")
            print("   then re-run.  (Drop --online to use the offline stub.)")
            return
        label = "quanta agent (Bedrock, local)"
    else:
        os.environ["QUANTA_STUB"] = "1"
        label = "quanta agent (offline stub)"

    from quanta.agent import invoke

    for q in questions:
        _cmd(f'{label} ← "{q}"')
        print(f"\n>>> {q}\n")
        try:
            print(invoke({"prompt": q})["result"])
        except Exception as exc:  # noqa: BLE001
            if not online:
                raise
            print(_c("33", f"   Bedrock call failed: {exc}"))
            print(
                "   Check AWS creds, AWS_REGION, and Bedrock model access "
                "(model id is in quanta/config.py)."
            )
            return
        _pause()


def do_scan(out: Path, no_install: bool) -> None:
    _step("Now turn Ziran on it — find what the tools can do *together*")
    # Prefer a sibling ../ziran checkout so the demo uses the latest source
    # (which surfaces tool-composition chains as findings), not a stale wheel.
    local_src = (ROOT.parent / "ziran" / "pyproject.toml").exists()
    if not no_install and (local_src or not _ziran_available()):
        _install_ziran()

    out.mkdir(parents=True, exist_ok=True)
    html: Path | None = None
    if _ziran_available():
        script = ROOT / "scripts" / "scan_quanta.py"
        _cmd(f"python scripts/{script.name} --out {out}")
        env = _child_env()
        env["QUANTA_STUB"] = "1"
        subprocess.run([sys.executable, str(script), "--out", str(out)], check=True, env=env)
        reports = sorted(out.glob("*_report.html"), key=lambda p: p.stat().st_mtime, reverse=True)
        html = reports[0] if reports else None
    else:
        print(_c("33", "   Ziran unavailable — opening the pre-generated report instead."))
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
    pa_mode = pa.add_mutually_exclusive_group()
    pa_mode.add_argument("--cloud", action="store_true", help="the deployed AgentCore agent")
    pa_mode.add_argument(
        "--online",
        action="store_true",
        help="real Strands+Bedrock, in-process (needs .[agentcore] + AWS creds)",
    )

    ps = sub.add_parser("scan", help="run Ziran and open the report")
    ps.add_argument("--out", type=Path, default=ROOT / "reports")
    ps.add_argument("--no-install", action="store_true", help="don't auto-install Ziran")

    sub.add_parser("exploit", help="run the breach + hardened fix")
    sub.add_parser("deploy", help="deploy to Amazon Bedrock AgentCore")
    pall = sub.add_parser("all", help="ask -> scan -> exploit (default)")
    pall_mode = pall.add_mutually_exclusive_group()
    pall_mode.add_argument("--cloud", action="store_true")
    pall_mode.add_argument("--online", action="store_true")
    pall.add_argument("--no-install", action="store_true")

    args = parser.parse_args()
    PAUSE = args.pause

    cmd = args.cmd or "all"
    if cmd == "ask":
        do_ask(args.questions or QUESTIONS, cloud=args.cloud, online=args.online)
    elif cmd == "scan":
        do_scan(args.out, args.no_install)
    elif cmd == "exploit":
        do_exploit()
    elif cmd == "deploy":
        do_deploy()
    else:  # all
        do_ask(
            QUESTIONS, cloud=getattr(args, "cloud", False), online=getattr(args, "online", False)
        )
        do_scan(ROOT / "reports", getattr(args, "no_install", False))
        do_exploit()


if __name__ == "__main__":
    main()
