# Deployment

Quanta deploys to **Amazon Bedrock AgentCore Runtime**. There are two ways to
deploy — both do the same thing; CI is recommended.

```
GitHub Actions (OIDC)                     AWS
  └─ agentcore configure                   ├─ CodeBuild  ──build image──▶ ECR
  └─ agentcore launch ───────────────────▶ ├─ AgentCore Runtime  ◀── exec role
  └─ agentcore invoke (smoke test)         └─ Bedrock (Claude model)
```

The container is built **in AWS CodeBuild**, so neither your laptop nor the CI
runner needs Docker.

## Architecture of the deploy

- **Entrypoint:** `quanta/agent.py` exposes `BedrockAgentCoreApp` with an
  `@app.entrypoint invoke(payload)` and serves the AgentCore contract via
  `app.run()`.
- **Image deps:** `requirements.txt` (kept in sync with the `agentcore` extra).
- **Data:** `quanta-load-data` builds the read-only `analytics.db` into the
  build context before launch, so the replica ships inside the image.
- **IAM:** provisioned once by the CDK app in `infra/` (see
  [`infra/README.md`](../infra/README.md)).

## 1. One-time bootstrap

Deploy the CDK stack and copy its outputs into GitHub repo variables — see
[`infra/README.md`](../infra/README.md):

```bash
cd infra
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cdk bootstrap        # one-time per account/region
cdk deploy           # prints DeployRoleArn + ExecutionRoleArn
```

You need these GitHub repo variables:

| GitHub repo variable | From |
|----------------------|------|
| `AWS_REGION` | the region you bootstrapped |
| `AWS_DEPLOY_ROLE_ARN` | stack output `DeployRoleArn` |
| `AGENTCORE_EXECUTION_ROLE_ARN` | stack output `ExecutionRoleArn` |

Also enable **Bedrock model access** for the Claude model
(`anthropic.claude-3-5-sonnet-*`) in that region (Bedrock console → *Model
access*).

## 2a. Deploy with GitHub Actions (recommended)

The [`Deploy to AgentCore`](../.github/workflows/deploy.yml) workflow runs on:

- pushes to `main` that touch `quanta/**`, `requirements.txt`, `pyproject.toml`,
  or the workflow file, and
- manual **Run workflow** (with an optional smoke prompt).

It authenticates to AWS via OIDC (no stored keys), builds the dataset,
configures + launches the agent, and runs a smoke `agentcore invoke`.

> The workflow targets a `production` GitHub *environment*. Create it (Settings →
> Environments) if you want a manual approval gate before each deploy.

## 2b. Deploy from your machine

```bash
pip install -e '.[agentcore]'
export AWS_REGION=us-east-1
export AGENTCORE_EXECUTION_ROLE_ARN=<ExecutionRoleArn>
aws sso login          # or aws configure — any creds that can assume nothing extra
python scripts/demo.py deploy
python scripts/demo.py ask --cloud
```

`python scripts/demo.py deploy` is intentionally identical in spirit to the CI
workflow (install toolkit → build data → configure → launch → status).

## 3. Verify

```bash
agentcore status
agentcore invoke '{"prompt": "What was our revenue by country last quarter? Top 5."}'
```

A useful, real answer here is the on-stage proof that Quanta is a working
assistant — *before* ZIRAN turns it red.

## Teardown

```bash
agentcore destroy                          # remove the runtime + ECR image
cd infra && source .venv/bin/activate && cdk destroy   # remove the IAM roles
```

## Toolkit version note

CLI flags can differ slightly across `bedrock-agentcore-starter-toolkit`
releases. If `agentcore configure` rejects a flag, run `agentcore configure
--help`; the meaningful inputs are always: entrypoint (`quanta/agent.py`),
name (`quanta`), region, execution role ARN, and requirements file.
