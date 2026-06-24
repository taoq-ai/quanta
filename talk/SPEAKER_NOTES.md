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
| 15 | What Ziran does | 0:25–0:26 | Build the graph |
| 16 | The graph, in three steps | 0:26–0:28 | graph-evolution |
| 17 | **The reveal** (overlay) | 0:28–0:30 | every box held |
| 18 | The real interactive graph (GIF) | 0:30–0:32 | **demo:** scan + graph |
| 19 | *Section 4:* From finding to breach | 0:32–0:33 | — |
| 20 | **Exploit, live** | 0:33–0:36 | **demo:** PII leaves |
| 21 | Three vulnerabilities, one agent | 0:36–0:38 | LLM01 + LLM06 + composition |
| 22 | **Hardened, live** | 0:38–0:40 | **demo:** same attack blocked |
| 23 | Break the graph | 0:40–0:41 | the four controls |
| 24 | What about multi-agent? | 0:41–0:43 | trifecta across agents |
| 25 | Breaking the graph across agents | 0:43–0:44 | system-level remediation |
| 26 | Close | 0:44–0:44 | thesis restated |
| 27 | Resources & disclaimer | 0:44–0:45 | links, Q&A |

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
  python scripts/demo.py ask --cloud      # the deployed AgentCore agent
  ```
- **Slide 18 — find the composition (live Ziran):**
  ```bash
  python scripts/demo.py scan             # installs Ziran if needed, scans, opens the report
  ```
  The slide embeds the real graph as a looping GIF — it plays in Presenter View and is the fallback if the live open stalls.
- **Slides 20 + 23 — the breach, then the fix:**
  ```bash
  python scripts/demo.py exploit          # prints both runs (vulnerable, then hardened)
  ```

### If wifi/AWS fails
Skip the slide-12 `--cloud` invoke; use `python scripts/demo.py ask` (offline).
The scan **and** the exploit run in-process and offline, so they never need the
network. The frozen GIF/PNGs in `talk/assets/` are the ultimate safety net.

---

## Two beats to nail
- **Slide 18 reveal (static + dynamic):** "I didn't tell Ziran this was dangerous — its built-in composition patterns did (static). And it's not theoretical: Ziran confirms the live exfil from the observed tool calls (dynamic). What it does NOT do — flag the agent merely listing its tools. The finding is the composition, not a keyword."
- **Slide 20 climax:** narrate the **taint column going red** — `PRIVATE+UNTRUSTED` forming in one run, then 16,741 bytes of PII leaving to a mailbox **on the allowlisted domain**. That single moment is the payoff. Then: "No control was bypassed."

**Timing guardrails:** if running long, trim slide 7 (two failure shapes) and keep the multi-agent pair (24–25) tight — slide 24 is the beat, slide 25 can be a quick read or held for Q&A. **Never cut the reveal (17–18) or the exploit (20, 22).** The multi-agent slides also double as a ready answer to "doesn't multi-agent solve this?"
