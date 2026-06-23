# Threat model

The thesis in one table: **every tool is individually defensible, and the
composition is still critical.**

## Per-tool controls vs. residual risk

| Tool | Declared control (passes review) | Residual risk (survives the control) |
|---|---|---|
| `search_database` | Read-only replica; parameterised query builder (no raw SQL); row cap; least-privilege IAM. | Its *legitimate* analytics scope includes customer-level rows (IDs, per-customer history, country). The data it is allowed to read is the data that must not leave. |
| `run_analysis` | Network-isolated sandbox; no imports; no filesystem; time limit. Not a general REPL. | A compute node reachable from untrusted input — only meaningful in composition, never alone. |
| `fetch_reference` | Egress **allowlist** on destination host. | The allowlist validates *where* the request goes, not *what* comes back. Returned content is untrusted and can carry an indirect prompt injection. **This is the entry point.** |
| `send_email_report` | Recipient-domain allowlist; append-only audit log; dry-run by default. | An allowlisted domain can still reach the wrong human; any data the model places in the body rides out through a legitimate, audited channel. **This is the exit.** |

None of the rows above is a finding on its own. A tool-by-tool review signs off
on all four.

## The composition (the actual finding)

```
            ┌─ fetch_reference ─ untrusted content (indirect prompt injection)
            ▼
  search_database ───────────────▶ send_email_report
  (reads private data)             (sends to allowlisted external channel)
        = CRITICAL data exfiltration  (ZIRAN: data_exfiltration, critical)
```

**Lethal trifecta:** private data + untrusted content + external communication,
all present in one agent. The attacker does not need to defeat any single
control. They need the *path*, and the path is authorised end-to-end.

## Three vulnerability classes, one agent

The composition is the *precondition*. Exploiting it pulls in two more classes
that live on the same four tools. All three are demonstrated by one runnable
attack (`scripts/exploit_demo.py`).

| # | Class | OWASP | Where it lives | Caught by |
|---|---|---|---|---|
| 1 | **Tool-composition data exfiltration** | — (structural) | `search_database → send_email_report` | ZIRAN `ToolChainAnalyzer` (static, pre-attack) |
| 2 | **Indirect prompt injection** | LLM01 | untrusted content from `fetch_reference` is followed as an instruction | the exploit / runtime policy |
| 3 | **Excessive agency / confused deputy** | LLM06 / LLM08 | `send_email_report` trusts a *model-chosen* recipient | the exploit / runtime policy |

Full walkthrough with the payload and the bytes that leave:
[`exploitation.md`](exploitation.md).

## What ZIRAN reports

Running `scripts/scan_quanta.py` builds the capability graph and runs ZIRAN's
`ToolChainAnalyzer`. It flags, from its **built-in** pattern library (not from
anything we label):

| Risk | Type | Path |
|---|---|---|
| 🔴 critical | `data_exfiltration` | `search_database → send_email_report` |

ZIRAN finds class #1 **statically, before anyone is attacked** — the structural
precondition. Classes #2 and #3 are the trigger and the missing control that
turn that precondition into a live breach.

## Mitigations (design-time, not per-tool)

The fix is not "remove a tool" — each is justified. It is to break the *graph*.
All three controls below are implemented and tested in
[`quanta/security/`](../quanta/security/policy.py); full code +
rationale in [`remediation.md`](remediation.md):

- **No instructions from data** — content from `fetch_reference` is data, never
  commands (kills LLM01).
- **Recipient binding** — `send_email_report` may only target the authenticated
  requester, not a model-chosen address, even an allowlisted one (kills LLM06).
- **Trifecta gate (taint):** a run holding both private data and untrusted
  content may not reach an external sink unattended. Aggregates are not marked
  private, so the legitimate task is unaffected.
- **Continuously re-scan:** treat the composition graph as a reviewable artifact
  in CI (`ziran ci`) so a newly-added tool that completes a trifecta fails the
  build.
