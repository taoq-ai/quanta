# Infrastructure (AWS CDK)

One-time IAM bootstrap for deploying Quanta to Amazon Bedrock AgentCore, as a
small **AWS CDK** app (Python).

The agent runtime itself is created by the **AgentCore CLI** (`agentcore
launch`, which builds the image in AWS CodeBuild). The only thing that must
exist beforehand is IAM — two roles — and that is what this CDK stack
provisions:

| Role | Assumed by | Purpose |
|------|------------|---------|
| `quanta-github-deploy` | GitHub Actions (via OIDC) | Run `agentcore launch` in CI |
| `AmazonBedrockAgentCore-quanta-exec` | the AgentCore runtime | The permissions the running agent has (invoke Bedrock, logs) |

It also creates the GitHub Actions OIDC provider
(`token.actions.githubusercontent.com`) unless you tell it one already exists.

```
infra/
  app.py                              # CDK app entry (python3 app.py)
  cdk.json                            # context defaults (org/repo/ref/model)
  requirements.txt                    # aws-cdk-lib, constructs
  stacks/quanta_bootstrap_stack.py    # the two roles + OIDC provider + outputs
```

## Prerequisites

- AWS CDK CLI: `npm install -g aws-cdk` (or use `npx aws-cdk`).
- Python 3.11+ and AWS credentials for the target account/region.

## Deploy

```bash
cd infra
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cdk bootstrap                  # one-time per account/region (CDK's own setup)
cdk deploy                     # creates the two roles; prints the ARNs
```

Customise via context (defaults live in `cdk.json`):

```bash
cdk deploy \
  -c github_org=taoq-ai \
  -c github_repo=quanta \
  -c github_ref='refs/heads/main' \      # restrict which refs may deploy ('*' = any)
  -c create_oidc_provider=false          # if the account already has the GitHub OIDC provider
```

Pin the account/region explicitly if your shell defaults differ:
`-c account=123456789012 -c region=us-east-1`.

## Wire up GitHub Actions

`cdk deploy` prints `DeployRoleArn` and `ExecutionRoleArn`. Set these as
**GitHub repository variables** (*Settings → Secrets and variables → Actions →
Variables*):

| Variable | Value |
|----------|-------|
| `AWS_REGION` | the region you deployed in (e.g. `us-east-1`) |
| `AWS_DEPLOY_ROLE_ARN` | `DeployRoleArn` output |
| `AGENTCORE_EXECUTION_ROLE_ARN` | `ExecutionRoleArn` output |

Then push to `main` (or run the *Deploy to AgentCore* workflow). See
[`../docs/deployment.md`](../docs/deployment.md) for the full flow and teardown.

## Teardown

```bash
cd infra && source .venv/bin/activate
cdk destroy
```

## Security note

This is an **educational demo**. The deploy role's policy is intentionally broad
(`bedrock-agentcore:*`, `ecr:*`) so `agentcore launch` works without manual
plumbing. Scope it down before any production use.
