"""Run Quanta locally (no AWS) — a quick smoke test of the assistant.

    QUANTA_STUB=1 PYTHONPATH=. python scripts/run_local.py
    QUANTA_STUB=1 PYTHONPATH=. python scripts/run_local.py "top customers by orders"
"""

from __future__ import annotations

import sys

from quanta.agent import invoke

PROMPTS = [
    "What is our revenue by country?",
    "Summarise orders by country and email me the report.",
]


def main() -> None:
    prompts = sys.argv[1:] or PROMPTS
    for p in prompts:
        print(f"\n>>> {p}\n")
        print(invoke({"prompt": p})["result"])


if __name__ == "__main__":
    main()
