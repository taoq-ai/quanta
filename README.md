# Quanta — a data-analyst agent that's *well-built* and still exploitable

> ### ⚠️ Educational use only — known intentional vulnerability
> Quanta is a **deliberately composable** Amazon Bedrock AgentCore agent for
> security education. Every tool is individually hardened, yet a graph-level
> data-exfiltration path survives by design. **Do not deploy as-is or connect it
> to real data.** See [`DISCLAIMER.md`](DISCLAIMER.md).

Quanta is the companion demo target for the talk **“When Your Agent Tools
Combine Against You”** and for [ZIRAN](https://github.com/taoq-ai/ziran). It
exists to make one point concrete:

> **The vulnerability lives in the graph, not in any node.**

Quanta is a believable analytics assistant. It answers questions like *“what was
our revenue by country?”* using four tools — each one individually defensible
and review-passing:

| Tool | What it does | Its control (declared defence) |
|---|---|---|
| `search_database` | reads business metrics | read-only replica + parameterised query builder + row cap |
| `run_analysis` | summarises results | network-isolated, import-less sandbox |
| `fetch_reference` | pulls external benchmarks | egress **allowlist** (destination only) |
| `send_email_report` | shares the report | recipient-domain allowlist + audit log + dry-run |

Tool by tool, this passes review. But an LLM agent can *sequence* its tools, and
ZIRAN's composition analysis finds the path no per-tool review catches:

```
search_database  ──▶  send_email_report      = CRITICAL data exfiltration
(private data)        (external channel)        (driven by untrusted content
                                                 from fetch_reference)
```

## See it exploited (and fixed) — no AWS

The composition is the *precondition*. One runnable attack turns it into a live
breach and stacks **three** vulnerability classes on the same four tools:

| # | Class | OWASP |
|---|---|---|
| 1 | Tool-composition data exfiltration | — (structural; ZIRAN finds it statically) |
| 2 | Indirect prompt injection | LLM01 |
| 3 | Excessive agency / confused deputy | LLM06 / LLM08 |

```bash
uv run python scripts/exploit_demo.py     # same agent, two policies, opposite outcomes
uv run pytest tests/test_exploit.py       # the lesson as assertions
```

A benign request — *"benchmark Q4 revenue and email me a summary"* — fetches a
reference whose content carries a hidden instruction. The **vulnerable** agent
follows it, reads ~900 customer-level rows, and emails ~16 KB of PII to an
attacker mailbox **on the allowlisted domain** (the domain check passes). The
**hardened** agent refuses the injected instruction, blocks the model-chosen
recipient, and still delivers the analyst's summary. Every per-tool control held
in both runs — only the design-time composition policy changed.

Walkthrough: [`docs/exploitation.md`](docs/exploitation.md) ·
Fixes: [`docs/remediation.md`](docs/remediation.md) ·
Threat model: [`docs/threat-model.md`](docs/threat-model.md)

## Architecture

Hexagonal (ports & adapters), kept deliberately small — see
[`docs/architecture.md`](docs/architecture.md) and the annotated diagram
[`docs/architecture.svg`](docs/architecture.svg).

```
quanta/
  domain/      ports (interfaces) + value objects — no I/O
  adapters/    one per tool; each enforces its control
  capabilities.py  the tool catalogue + data-flow surface (single source of truth)
  tools.py     thin callables wired to adapters
  agent.py     BedrockAgentCoreApp entrypoint (Strands+Bedrock, or local stub)
```

## Quickstart (local, no AWS)

```bash
pip install -e '.[data,dev]'

# 1. Build the read-only analytics replica (real UCI dataset; --synthetic for offline)
quanta-load-data            # or: quanta-load-data --synthetic

# 2. Run the assistant locally (deterministic stub — no Bedrock needed)
QUANTA_STUB=1 PYTHONPATH=. python scripts/run_local.py

# 3. Scan it with ZIRAN — see the composition finding + interactive report
QUANTA_STUB=1 PYTHONPATH=. python scripts/scan_quanta.py --out reports
open reports/*.html

# 4. Watch the composition get exploited, then blocked by the hardened policy
python scripts/exploit_demo.py
```

## Deploy for real (Amazon Bedrock AgentCore)

Infrastructure-as-code and CI/CD live in [`infra/`](infra/) and
[`.github/workflows/`](.github/workflows/). Full guide:
[`docs/deployment.md`](docs/deployment.md).

**One-time IAM bootstrap** (AWS CDK — creates a GitHub-OIDC deploy role and the
AgentCore runtime execution role):

```bash
cd infra
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cdk bootstrap          # one-time per account/region
cdk deploy             # prints DeployRoleArn + ExecutionRoleArn
# Copy the two output ARNs into GitHub repo variables (see docs/deployment.md).
```

**Deploy via GitHub Actions** (recommended) — push to `main` or run the
*Deploy to AgentCore* workflow. The image is built in AWS CodeBuild (no Docker),
then `agentcore launch` + a smoke `agentcore invoke` run automatically.

**Deploy from your machine:**

```bash
pip install -e '.[agentcore]'
export AGENTCORE_EXECUTION_ROLE_ARN=<ExecutionRoleArn from the bootstrap stack>
./scripts/deploy.sh          # agentcore configure + launch (CodeBuild build)
./scripts/invoke_demo.sh     # prove it's a real, working assistant
```

The ZIRAN scan runs **in-process**, so the live demo never depends on the
deployed endpoint being reachable — deployment is for credibility, the scan is
for the reveal.

## Dataset

Bundled queries run against the public **UCI Online Retail II** dataset
(Chen, 2019). Provenance, citation, and the replica schema:
[`docs/data.md`](docs/data.md).

## Talk materials

Slides, speaker notes, and visual aids live in [`talk/`](talk/).

## License

MIT, with an educational-use notice — see [`LICENSE`](LICENSE).
