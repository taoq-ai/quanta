#!/usr/bin/env bash
# Deploy Quanta to Amazon Bedrock AgentCore Runtime.
#
# Prerequisites:
#   - AWS credentials with Bedrock + AgentCore access (`aws configure`)
#   - Bedrock model access enabled for the Claude model in $AWS_REGION
#   - Docker running (AgentCore builds a container)
#   - pip install -e '.[agentcore]'
#
# This makes the demo REAL: Quanta runs as a managed AgentCore agent you can
# invoke live on stage. The ZIRAN scan itself runs in-process (scan_quanta.py),
# so the demo does not depend on the runtime endpoint being reachable.
set -euo pipefail

export AWS_REGION="${AWS_REGION:-us-east-1}"

echo "==> Configuring AgentCore (entrypoint: quanta/agent.py)"
agentcore configure -e quanta/agent.py --name quanta

echo "==> Launching to AgentCore Runtime in ${AWS_REGION}"
agentcore launch

echo "==> Done. Try: ./scripts/invoke_demo.sh"
