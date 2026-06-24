# Speaker notes — *When Your Agent Tools Combine Against You*

**Length:** 45 min (≈30 min talk + ≈10 min live demo + ≈5 min Q&A)
**Audience:** builders / engineers
**Demo target:** Quanta (Amazon Bedrock AgentCore) · **Finder:** Ziran
**One sentence:** *Individually-safe tools compose into an exfiltration path; the vulnerability lives in the graph, and you can find it before an attacker does.*

> **Full per-slide notes are embedded in the deck** (`talk/quanta-talk.pptx` → Presenter View, or View ▸ Notes). This file is the at-a-glance arc + the live-demo runbook.
> Live driver (one Python script, no shell): `python scripts/demo.py` — subcommands `ask`, `scan`, `exploit`, `deploy`.
> Frozen fallbacks in `talk/assets/`: `ziran_graph.gif`, `ziran_report_dashboard.png`, `exploit_vulnerable.png`, `exploit_hardened.png`.

---

## Arc & timing

| # | Slide | Time | Beat |
|---|---|---|---|
| 1 | Title | 0:00–0:01 | — |
| 2 | Everyone watches the prompt | 0:01–0:03 | Cold open |
| 3 | A review sees a list; an agent has a graph | 0:03–0:05 | Reframe |
| 4 | *Section 1:* How an attacker navigates an agent | 0:05–0:06 | — |
| 5 | The attacker's mental model | 0:06–0:09 | Recon → map → chain |
| 6 | The lethal trifecta | 0:09–0:12 | Composition |
| 7 | Two failure shapes: exfil & RCE | 0:12–0:14 | Composition |
| 8 | Why reviews miss it | 0:14–0:16 | Blindness |
| 9 | *Section 2:* Meet the target | 0:16–0:17 | — |
| 10 | **Solution design (C4)** | 0:17–0:19 | Defensible design |
| 11 | …and notice it's well-built | 0:19–0:21 | Controls; "passes review" |
| 12 | Quanta, live | 0:21–0:23 | **demo:** real agent |
| 13 | Four tools, four controls | 0:23–0:24 | 4 / 4 approved |
| 14 | *Section 3:* Find the composition | 0:24–0:25 | — |
| 15 | Meet Ziran | 0:25–0:26 | what it is (informative, no pitch) |
| 16 | What Ziran does | 0:26–0:27 | Build the graph |
| 17 | The graph, in three steps | 0:27–0:28 | graph-evolution |
| 18 | **The reveal** (overlay) | 0:28–0:30 | every box held |
| 19 | The real interactive graph (GIF) | 0:30–0:32 | **demo:** scan + graph |
| 20 | *Section 4:* From finding to breach | 0:32–0:33 | — |
| 21 | **Exploit, live** | 0:33–0:36 | **demo:** PII leaves |
| 22 | Three vulnerabilities, one agent | 0:36–0:38 | LLM01 + LLM06 + composition |
| 23 | **Hardened, live** | 0:38–0:40 | **demo:** same attack blocked |
| 24 | Break the graph | 0:40–0:41 | the four controls |
| 25 | What about multi-agent? | 0:41–0:43 | trifecta across agents |
| 26 | Breaking the graph across agents | 0:43–0:44 | system-level remediation |
| 27 | Close | 0:44–0:44 | thesis restated |
| 28 | Resources & disclaimer | 0:44–0:45 | links, Q&A |

---

## Live demo runbook (rehearse this)

The whole demo is **one Python script** — `python scripts/demo.py` — or run the
pieces by hand. `ask` and `exploit` work offline on a bare checkout; `scan`
needs Ziran and installs it for you. Only `ask --cloud` uses AWS.

### Pre-flight (before you walk on)
1. `quanta-load-data` (real UCI data; `--synthetic` if no network).
2. If demoing the deployed agent: `python scripts/demo.py deploy` done earlier; confirm `python scripts/demo.py ask --cloud` answers.
3. Warm the scan once: `python scripts/demo.py scan` (installs Ziran, opens the HTML).
4. Open background tabs: `reports/*_report.html`, and the frozen `talk/assets/ziran_graph.gif`.

### One-command path
```bash
python scripts/demo.py --pause      # steps through: 3 real questions → live scan → exploit → fix
# add --cloud to use the deployed AgentCore agent for the questions.
```

### By hand (mapped to slides)
- **Slide 12 — it's a real agent:**
  ```bash
  python scripts/demo.py ask              # offline stub (3 questions)
  python scripts/demo.py ask --online     # real Bedrock, in-process (no deploy)
  python scripts/demo.py ask --cloud      # the deployed AgentCore agent
  ```
- **Slide 19 — find the composition (live Ziran):**
  ```bash
  python scripts/demo.py scan             # installs Ziran if needed, scans, opens the report
  ```
  The slide embeds the real graph as a looping GIF — it plays in Presenter View and is the fallback if the live open stalls.
- **Slides 21 + 23 — the breach, then the fix:**
  ```bash
  python scripts/demo.py exploit --vulnerable-only   # slide 21 (the breach)
  python scripts/demo.py exploit --hardened-only     # slide 23 (the fix)
  # …or `exploit` alone prints both runs back-to-back
  ```

### If wifi/AWS fails
Skip the slide-12 `--cloud` invoke; use `python scripts/demo.py ask` (offline).
The scan **and** the exploit run in-process and offline, so they never need the
network. The frozen GIF/PNGs in `talk/assets/` are the ultimate safety net.

---

## Two beats to nail
- **Slide 19 reveal (static + dynamic):** "I didn't tell Ziran this was dangerous — its built-in composition patterns did (static). And it's not theoretical: Ziran confirms the live exfil from the observed tool calls (dynamic). What it does NOT do — flag the agent merely listing its tools. The finding is the composition, not a keyword."
- **Slide 21 climax:** narrate the **taint column going red** — `PRIVATE+UNTRUSTED` forming in one run, then the **full customer list (names + emails)** leaving to a mailbox **on the allowlisted domain**. That single moment is the payoff. Then: "No control was bypassed."
- **Likely Q&A — "it says VULNERABLE but 0 vulnerabilities?"** That counter is *prompt-level* attack findings (the focused scan skips those phases). The real finding is the **critical composition** in the "Dangerous Tool Chains" section — that's what flips the verdict to VULNERABLE. The composition *is* the vulnerability.

## Policy beat — how the fix is applied (slides 21 & 23)
Both runs are the **same agent, tools, prompt, and injection** — the only change is one object passed into the agent loop: the **policy** (`exploit.py` → `HardenedPolicy() if hardened else PermissivePolicy()`). Say that out loud; it's the whole thesis.

**How it's applied:** the policy is two checkpoints *inside* the loop, not an outside filter. Before the agent obeys any instruction it found in fetched content it calls `review_external_instruction(...)`; before any outbound send it calls `review_delivery(recipient, requester, taint)`. Permissive says *yes* to both (a normal agent). Hardened applies three rules:
1. **No instructions from data** — `fetch_reference` content is data, never commands → kills indirect prompt injection (LLM01).
2. **Recipient binding** — email only to the authenticated requester, never a model/injection-chosen address → kills confused deputy / excessive agency (LLM06).
3. **Trifecta gate** — a run holding *both* private + untrusted data can't reach an external sink unattended → kills the composition itself.

**Narrate the hardened table row by row:**
- *step 1* `fetch_reference (untrusted)` → the taint tracker stamps it `UNTRUSTED`, and it sticks for the whole run.
- *step 3* `(policy) ignored injected instruction` → **Rule 1 firing**: the hidden instruction came from data, so it's refused *as data*; the malicious customer-data query never runs.
- point at the taint column: because that step was refused, the run **never picks up `PRIVATE`** — it stays `UNTRUSTED`, so the trifecta never forms (Rule 3 doesn't even need to fire).
- *step 4* `delivered (dry-run)` → the agent still emails the analyst their summary; that passes **Rule 2** (recipient == requester).
- `✓ BLOCKED` → injection neutralised, legitimate work still completed.

**Contrast with the vulnerable run:** same two checkpoints, opposite answers — permissive says *yes* at step 3 → the agent reads the **customer table (names + emails)** → taint goes **`PRIVATE+UNTRUSTED`** (red) → ships it to the attacker mailbox.

**Closing line:** "I didn't patch a tool or rewrite a prompt — I added a policy over the *composition*, and the same attack now does nothing. The vulnerability lived in the graph; so does the fix."

**Timing guardrails:** if running long, trim slide 7 (two failure shapes) and keep the multi-agent pair (25–26) tight — slide 25 is the beat, slide 26 can be a quick read or held for Q&A. **Never cut the reveal (18–19) or the exploit (21, 23).** The Meet-Ziran slide (15) can drop to one sentence if time is short. The multi-agent slides also double as a ready answer to "doesn't multi-agent solve this?"
