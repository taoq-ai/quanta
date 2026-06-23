#!/usr/bin/env python3
"""CDK app — one-time IAM bootstrap for deploying Quanta to Amazon Bedrock AgentCore.

Synthesises a single stack with two roles:
  - a GitHub-OIDC deploy role assumed by GitHub Actions to run `agentcore launch`, and
  - the AgentCore runtime execution role the agent assumes at runtime.

Deploy:
    cd infra
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    cdk bootstrap          # one-time per account/region
    cdk deploy
"""

from __future__ import annotations

import aws_cdk as cdk
from stacks.quanta_bootstrap_stack import QuantaBootstrapStack

app = cdk.App()

QuantaBootstrapStack(
    app,
    "QuantaBootstrap",
    description="IAM bootstrap (GitHub-OIDC deploy role + AgentCore execution role) for Quanta.",
    env=cdk.Environment(
        account=app.node.try_get_context("account") or None,
        region=app.node.try_get_context("region") or None,
    ),
    # IAM-only stack with no assets -> deploy directly with the caller's
    # credentials; no `cdk bootstrap` (and no bootstrap ECR/S3) required. This
    # also works in accounts whose SCPs deny ECR.
    synthesizer=cdk.CliCredentialsStackSynthesizer(),
)

app.synth()
