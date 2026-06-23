#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Live talk demo driver — run this on stage.
#
#   Part 1: prove Quanta is a real, useful agent  (3 analytics questions)
#   Part 2: turn ZIRAN on it, live                (find the composition)
#   Part 3 (optional): show the breach + the fix  (scripts/exploit_demo.py)
#
# Usage:
#   ./scripts/demo_live.sh            # auto: cloud if agentcore is set up, else local
#   MODE=cloud ./scripts/demo_live.sh # force the deployed AgentCore agent (real AWS)
#   MODE=local ./scripts/demo_live.sh # force the offline stub (no AWS)
#   PAUSE=1 ./scripts/demo_live.sh    # wait for <enter> between steps (good on stage)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")/.."

MODE="${MODE:-auto}"
PAUSE="${PAUSE:-0}"

step() { printf '\n\033[1;36m== %s\033[0m\n' "$*"; }
run()  { printf '\033[2m$ %s\033[0m\n' "$*"; }
pause() { [ "$PAUSE" = "1" ] && read -r -p $'\033[2m   …press enter…\033[0m' _ || true; }

if [ "$MODE" = "auto" ]; then
  if command -v agentcore >/dev/null 2>&1 && agentcore status >/dev/null 2>&1; then MODE=cloud; else MODE=local; fi
fi
echo "demo mode: ${MODE}"

ask_cloud() { run "agentcore invoke '{\"prompt\": \"$1\"}'"; agentcore invoke "{\"prompt\": \"$1\"}"; }
ask_local() { run "QUANTA_STUB=1 python scripts/run_local.py \"$1\""; QUANTA_STUB=1 PYTHONPATH=. python scripts/run_local.py "$1"; }
ask() { if [ "$MODE" = "cloud" ]; then ask_cloud "$1"; else ask_local "$1"; fi; }

# ── Part 1 — it's a real agent ───────────────────────────────────────────────
step "1/3  Quanta is a real analytics assistant"
ask "What was our revenue by country? Give me the top 5."; pause
ask "How many orders did we get per country?"; pause
ask "Who are our top customers by number of orders?"; pause

# ── Part 2 — find the composition, live ──────────────────────────────────────
step "2/3  Now turn ZIRAN on it — find what the tools can do *together*"
if python -c "import ziran" >/dev/null 2>&1; then
  run "QUANTA_STUB=1 python scripts/scan_quanta.py --out reports"
  QUANTA_STUB=1 PYTHONPATH=. python scripts/scan_quanta.py --out reports
  HTML="$(ls -t reports/*_report.html 2>/dev/null | head -1 || true)"
else
  printf '   \033[33mZIRAN is not installed — skipping the live scan.\033[0m\n'
  echo "   install:  pip install 'ziran[agentcore]'   (or: pip install -e ../ziran)"
  echo "   opening the pre-generated report instead."
  HTML="reports/quanta_scan_report.html"
fi
if [ -n "${HTML:-}" ] && [ -f "${HTML}" ]; then
  run "open ${HTML}"; (open "${HTML}" 2>/dev/null || xdg-open "${HTML}" 2>/dev/null || true)
fi
pause

# ── Part 3 — the breach and the fix (optional) ───────────────────────────────
step "3/3  (optional) watch the composition get exploited, then blocked"
run "python scripts/exploit_demo.py"
PYTHONPATH=. python scripts/exploit_demo.py

echo; echo "done."
