# ⚠️ Educational Use Only — Known Intentional Vulnerability

**Quanta is a deliberately composable AI agent built for security education and
research.** It is the companion demo target for the talk *"When Your Agent Tools
Combine Against You"* and for [ZIRAN](https://github.com/taoq-ai/ziran).

## What is intentional here

Quanta is **not** a careless toy. It is *deliberately well-architected*: every
tool is individually hardened and would pass a normal, tool-by-tool security
review (read-only data replica, sandboxed compute, egress allowlist, audited
delivery — see [`docs/threat-model.md`](docs/threat-model.md)).

The point of the project is exactly that this is **not enough**. A known,
**graph-level data-exfiltration path** survives the clean architecture:

> `search_database` (private data) → `send_email_report` (external channel)

driven by untrusted content entering through `fetch_reference`. No single tool
is the bug. The composition is. This is the *lethal trifecta* — private data +
untrusted content + external communication — realised despite defensible
controls.

## Do NOT

- ❌ Deploy this as a real product or expose it to real users.
- ❌ Connect it to real customer data, real email/delivery, or real secrets.
- ❌ Remove the `dry_run` / allowlist guards and point it at the internet.

## Do

- ✅ Run it locally and scan it with ZIRAN to *see* the composition risk.
- ✅ Use it to teach how attackers navigate an agent's tool graph.
- ✅ Adapt the architecture diagram for your own threat-modelling.

The bundled dataset is the public **UCI Online Retail II** dataset (see
[`docs/data.md`](docs/data.md)) — it contains no real personal data of your
users, but is treated as "sensitive" within the demo's narrative.
