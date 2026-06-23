#!/usr/bin/env bash
# Invoke the deployed Quanta agent — proof on stage that it is a real, working
# analytics assistant before we turn ZIRAN on it.
set -euo pipefail

PROMPT="${1:-What was our revenue by country last quarter? Give me the top 5.}"

echo "==> Invoking deployed Quanta with: ${PROMPT}"
agentcore invoke "{\"prompt\": \"${PROMPT}\"}"
