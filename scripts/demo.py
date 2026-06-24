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
    editable = (local / "pyproject.toml").exists()
    target = str(local) if editable else "ziran[agentcore]>=0.37.0"
    # uv-created venvs have no `pip`, so `python -m pip` silently fails and
    # leaves any stale wheel in place. Prefer `uv pip` when uv is on PATH so a
    # sibling ../ziran checkout (with the composition-findings API the scan
    # needs) actually installs and replaces an older pinned wheel.
    if shutil.which("uv"):
        args = ["uv", "pip", "install", "--python", sys.executable]
        shown = "uv pip install"
    else:
        args = [sys.executable, "-m", "pip", "install"]
        shown = "pip install"
    args += ["-e", target] if editable else [target]
    _cmd(f"{shown} {('-e ' + str(local)) if editable else repr(target)}")
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
            print(_c("33", "   --online needs the agentcore extra + AWS credentials. Easiest:"))
            print("     uv run --extra agentcore python scripts/demo.py ask --online")
            print("   (or install it once:  uv pip install -e '.[agentcore]')")
            print(
                "   AWS:  aws sso login --profile <profile>   ·   export AWS_PROFILE / AWS_REGION"
            )
            print("   (Drop --online to use the offline stub.)")
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
    # --pause on a shared parent so it works before OR after the subcommand
    # (SUPPRESS so an absent subparser copy doesn't clobber a value set earlier).
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--pause",
        action="store_true",
        default=argparse.SUPPRESS,
        help="wait for <enter> between steps",
    )
    # --online/--cloud accepted on every subcommand so habitual flag use never
    # crashes mid-demo. Only ask/all act on them; scan/exploit run the offline
    # deterministic harness and note the flag is ignored. SUPPRESS so an absent
    # subparser copy doesn't clobber a value set before the subcommand.
    mode = common.add_mutually_exclusive_group()
    mode.add_argument(
        "--online",
        action="store_true",
        default=argparse.SUPPRESS,
        help="ask/all: real Strands+Bedrock, in-process (needs .[agentcore] + AWS creds)",
    )
    mode.add_argument(
        "--cloud",
        action="store_true",
        default=argparse.SUPPRESS,
        help="ask/all: the deployed AgentCore agent",
    )
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[common],
    )
    sub = parser.add_subparsers(dest="cmd")

    pa = sub.add_parser("ask", parents=[common], help="run the analytics questions")
    pa.add_argument("questions", nargs="*")

    ps = sub.add_parser("scan", parents=[common], help="run Ziran and open the report")
    ps.add_argument("--out", type=Path, default=ROOT / "reports")
    ps.add_argument("--no-install", action="store_true", help="don't auto-install Ziran")

    sub.add_parser("exploit", parents=[common], help="run the breach + hardened fix")
    sub.add_parser("deploy", parents=[common], help="deploy to Amazon Bedrock AgentCore")
    pall = sub.add_parser("all", parents=[common], help="ask -> scan -> exploit (default)")
    pall.add_argument("--no-install", action="store_true")

    args = parser.parse_args()
    PAUSE = getattr(args, "pause", False)
    online = getattr(args, "online", False)
    cloud = getattr(args, "cloud", False)

    def _note_offline() -> None:
        if online or cloud:
            print(
                _c(
                    "33",
                    "   note: this step runs the offline deterministic harness — "
                    "--online/--cloud ignored here.",
                )
            )

    cmd = args.cmd or "all"
    if cmd == "ask":
        do_ask(args.questions or QUESTIONS, cloud=cloud, online=online)
    elif cmd == "scan":
        _note_offline()
        do_scan(args.out, args.no_install)
    elif cmd == "exploit":
        _note_offline()
        do_exploit()
    elif cmd == "deploy":
        do_deploy()
    else:  # all
        do_ask(QUESTIONS, cloud=cloud, online=online)
        do_scan(ROOT / "reports", getattr(args, "no_install", False))
        do_exploit()


if __name__ == "__main__":
    main()
