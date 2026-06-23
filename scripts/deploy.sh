#!/usr/bin/env bash
# Deploy Quanta to Amazon Bedrock AgentCore Runtime from your machine.
#
# This mirrors the GitHub Actions workflow (.github/workflows/deploy.yml) so a
# local deploy and a CI deploy do the same thing. The container image is built
# in AWS CodeBuild — no local Docker required.
#
# Prerequisites:
#   - AWS credentials with deploy permissions (`aws configure` / SSO), OR run
#     the GitHub Actions workflow instead (recommended).
#   - One-time IAM bootstrap applied: see infra/README.md.
#   - Bedrock model access enabled for the Claude model in $AWS_REGION.
#
# Environment:
#   AWS_REGION                    (default: us-east-1)
#   AGENTCORE_EXECUTION_ROLE_ARN  runtime execution role (from the bootstrap
#                                 stack output). If unset, `agentcore configure`
#                                 will offer to create one interactively.
#
# The ZIRAN scan itself runs in-process (scripts/scan_quanta.py), so the live
# demo does not depend on this deployment being reachable.
set -euo pipefail

export AWS_REGION="${AWS_REGION:-us-east-1}"

echo "==> Ensuring AgentCore CLI is installed"
command -v agentcore >/dev/null 2>&1 || pip install bedrock-agentcore-starter-toolkit

echo "==> Building analytics replica (UCI Online Retail II -> analytics.db)"
command -v quanta-load-data >/dev/null 2>&1 && quanta-load-data || python -m quanta.data_loader

echo "==> Configuring AgentCore (entrypoint: quanta/agent.py)"
configure_args=(
  --entrypoint quanta/agent.py
  --name quanta
  --region "$AWS_REGION"
  --requirements-file requirements.txt
  --non-interactive
)
if [[ -n "${AGENTCORE_EXECUTION_ROLE_ARN:-}" ]]; then
  configure_args+=(--execution-role "$AGENTCORE_EXECUTION_ROLE_ARN")
fi
agentcore configure "${configure_args[@]}"

echo "==> Launching to AgentCore Runtime in ${AWS_REGION} (CodeBuild build)"
agentcore launch

echo "==> Status"
agentcore status || true

echo "==> Done. Try: ./scripts/invoke_demo.sh"
