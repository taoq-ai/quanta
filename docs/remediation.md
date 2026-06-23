# How to remediate

The wrong fix is "remove a tool" — each one is justified, and the product needs
all four. The right fix is to **break the graph**: stop the *path* without
crippling the agent. In Quanta this is one injected
[`SecurityPolicy`](../quanta/security/policy.py); the agent loop is unchanged.

Run both outcomes side by side:

```bash
uv run python scripts/exploit_demo.py     # vulnerable run, then hardened run
```

The hardened agent **blocks the exfiltration and still completes the legitimate
task**. Three layered controls, each killing one of the stacked vulnerability
classes.

## 1. Never treat fetched content as instructions (kills LLM01)

Content returned by `fetch_reference` is **data, never commands**. The hardened
policy refuses to act on any instruction whose origin is untrusted:

```python
def review_external_instruction(self, directive, *, source_trusted):
    if not source_trusted:                       # came from fetch_reference()
        return Decision(False, "ignored as data", "no-instructions-from-data (LLM01)")
    ...
```

In the demo this alone stops the attack at step 3 — the injected "export
customers" instruction is dropped before any PII is read.

## 2. Bind the recipient to the authenticated user (kills LLM06 / confused deputy)

`send_email_report` must not send to a *model-chosen* address — even an
allowlisted one. It may only reach the person who made the request:

```python
def review_delivery(self, recipient, *, requester, taint):
    if recipient.lower() != requester.lower():
        return Decision(False, f"{recipient} is not the requester", "recipient-binding (LLM06)")
    ...
```

This is the control the domain allowlist was mistaken for. A domain check asks
"is this address shaped right?". Recipient binding asks "is this the user we are
acting on behalf of?" — the question that actually matters.

## 3. Gate the lethal trifecta (defence in depth)

Track taint across the run. A run that holds **both** private data (`PRIVATE`)
and untrusted content (`UNTRUSTED`) must not reach an external sink unattended:

```python
if taint.holds_trifecta():        # PRIVATE + UNTRUSTED both present
    return Decision(False, "lethal trifecta; external send needs human review", "trifecta-gate")
```

Note the deliberate nuance: **aggregate** metrics (revenue by country) are not
marked `PRIVATE`, only **customer-level** rows are. So the legitimate task —
benchmark + aggregate revenue + email the requester — never trips the gate. A
gate that breaks the product gets switched off; this one doesn't.

## Putting it in the pipeline

| Control | Stops | OWASP | Cost to the product |
|---|---|---|---|
| No-instructions-from-data | indirect prompt injection | LLM01 | none — content was never meant to command |
| Recipient binding | confused deputy / excessive agency | LLM06/LLM08 | none — users email themselves |
| Trifecta gate (taint) | composition exfiltration | structural | low — only customer-level + external send needs review |
| **ZIRAN in CI** (`ziran ci`) | a *new* tool silently completing a trifecta | structural | a failed build, before deploy |

The first three are runtime guardrails. The last is the design-time one that
matches the talk's thesis: treat the **composition graph** as a reviewable
artifact, and fail the build when a newly added tool turns three safe
capabilities into an exfiltration path. See the ZIRAN scan in
[`scripts/scan_quanta.py`](../scripts/scan_quanta.py) and the
[`23-quanta-agentcore`](https://github.com/taoq-ai/ziran/tree/main/examples)
example.
