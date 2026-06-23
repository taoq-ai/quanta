# Speaker notes — *When Your Agent Tools Combine Against You*

**Length:** 45 min (≈33 min talk + ≈8 min live demo + ≈4 min Q&A)
**Audience:** builders / engineers
**Demo target:** Quanta (Amazon Bedrock AgentCore) · **Finder:** ZIRAN
**One sentence:** *Individually-safe tools compose into an exfiltration path; the vulnerability lives in the graph, and you can find it before an attacker does.*

> Deck: `talk/quanta-talk.pptx` · assets: `talk/assets/` · live driver: `scripts/scan_quanta.py` · frozen fallback: `talk/assets/ziran_report_dashboard.png` + `reports/quanta_scan_report.html`.

---

## Arc & timing

| # | Slide | Time | Beat |
|---|---|---|---|
| 1 | Title | 0:00–0:01 | — |
| 2 | "Everyone watches the prompt" | 0:01–0:03 | Cold open |
| 3 | Tools aren't a list — they're a graph | 0:03–0:06 | Reframe |
| 4 | *Section:* How an attacker navigates an agent | 0:06–0:07 | — |
| 5 | The attacker's mental model | 0:07–0:12 | Recon → map → chain |
| 6 | The lethal trifecta | 0:12–0:16 | Composition |
| 7 | Two failure shapes: exfil & RCE | 0:16–0:19 | Composition |
| 8 | Why reviews miss it | 0:19–0:23 | Blindness |
| 9 | *Section:* Meet the target | 0:23–0:24 | — |
| 10 | Quanta — a *well-built* agent | 0:24–0:27 | Defensible architecture |
| 11 | Quanta, live | 0:27–0:29 | It really works |
| 12 | Four tools, four controls | 0:29–0:30 | "This passes review" |
| 13 | *Section:* Live — find the composition | 0:30–0:31 | — |
| 14 | What ZIRAN does | 0:31–0:33 | Build the graph |
| 15 | The graph, in three steps | 0:33–0:35 | graph-evolution |
| 16 | **The reveal** | 0:35–0:38 | overlay — every box held |
| 17 | The real report | 0:38–0:40 | ZIRAN dashboard + graph |
| 18 | What's behind the scan | 0:40–0:41 | credibility |
| 19 | What to do about it | 0:41–0:43 | design-time graph review |
| 20 | Close | 0:43–0:44 | thesis restated |
| 21 | Resources & disclaimer | 0:44–0:45 | links, Q&A |

---

## Per-slide notes

### 1 — Title
Land the title, then a beat. "By the end you'll have watched a clean, well-architected agent get one critical finding — and the finding isn't in any of its tools."

### 2 — Everyone watches the prompt
Most AI-security energy goes at the prompt: jailbreaks, injection, guardrails. It matters — but it's the part everyone is already looking at. **Say:** "I want to talk about the risk nobody's looking at, because it isn't visible from where they're standing."

### 3 — Tools aren't a list, they're a graph
A security review enumerates tools like API endpoints: a *list*. But an LLM agent can call any tool, then feed its output into the next. That's not a list — it's a **graph of what the agent can do next**. Hold this idea; the whole talk turns on it.

### 4 — Section: How an attacker navigates an agent
Divider. "Forget the model for a minute. Think like someone who just got access to the agent."

### 5 — The attacker's mental model
Three moves: **recon** (what tools exist?), **capability mapping** (what does each touch — data? network? compute?), **chaining** (which sequence turns reasonable actions into one bad outcome?). Attackers don't look for *a* dangerous tool. They look for a *path*. This is graph traversal, done by hand.

### 6 — The lethal trifecta  *(lethal-trifecta.png)*
Three capabilities that are individually fine and collectively lethal: **access to private data**, **exposure to untrusted content**, **the ability to communicate externally**. Any agent with all three can be steered to read secrets and send them out — through entirely authorised actions. Credit the framing (Simon Willison's "lethal trifecta").

### 7 — Two failure shapes
Same structural idea, two shapes. **Exfiltration:** read + send. **RCE surface:** fetch untrusted + execute + network. Neither is a bug in a node. Both are properties of the *graph*.

### 8 — Why reviews miss it  *(review-blindness.png)*
Reviews look tool-by-tool, endpoint-by-endpoint — and tool-by-tool, everything passes. The composition is invisible from that vantage point. **Say:** "It stays invisible until someone connects the dots. The only question is whether that someone works for you."

### 9 — Section: Meet the target
Divider. "Let me show you an agent I built — and I want you to try to find the problem while I describe it."

### 10 — Quanta, a well-built agent  *(architecture.png)*
Quanta is a data-analyst assistant on Amazon Bedrock AgentCore. Walk the architecture: **hexagonal**, read-only analytics replica, **parameterised** queries (no raw SQL), a **sandboxed** interpreter with no network, an **egress allowlist** on outbound fetches, **audited** report delivery. **Say:** "This is not a toy. Every box here is something you'd sign off on. There is no unsandboxed `eval`, no raw SQL, no open egress."

### 11 — Quanta, live
Switch to terminal. `./scripts/invoke_demo.sh` (or `agentcore invoke`) — ask *"revenue by country, top 5."* It answers with real numbers from the UCI Online Retail II dataset. **Say:** "Real agent, real data, genuinely useful. Now — is it safe?"

### 12 — Four tools, four controls
The table: `search_database` (read-only, parameterised), `run_analysis` (sandboxed), `fetch_reference` (allowlist), `send_email_report` (allowlist + audit + dry-run). **Say:** "Four tools. Four real controls. A tool-by-tool review signs off 4 out of 4. Hold that thought."

### 13 — Section: Live — find the composition
Divider. "Instead of reviewing tools one at a time, let's look at what they can do *together*."

### 14 — What ZIRAN does
ZIRAN builds the agent's capability graph and checks it against a library of known dangerous compositions — direct (A→B), indirect (A→…→B), and cycles. **Say:** "It's not testing prompts here. It's reasoning about structure."

### 15 — The graph in three steps  *(graph-evolution.png)*
Walk the three panels: four approved tools → the agent can sequence them (edges) → one path is an exit. **Say:** "Nothing here is hypothetical. An LLM agent really can call send right after search."

### 16 — THE REVEAL  *(architecture-overlay.png)*
Back to the architecture — now with the red path. **Say slowly:** "Every control still holds. Read-only: held. Sandbox: held. Allowlists: held. And here's the path: untrusted content comes in through `fetch_reference`, the agent reads private data with `search_database`, and ships it out through `send_email_report` — every step authorised. Every box was hardened. The arrow wasn't."

### 17 — The real report  *(ziran_report_dashboard.png)*
This isn't a slide drawing — this is the scan output. **Live:** run `scripts/scan_quanta.py`, open the HTML. One critical finding: `search_database → send_email_report`, `data_exfiltration`. Click the red node in the graph. **Fallback:** if anything stalls, this screenshot is the same result. **Say:** "I didn't tell ZIRAN this was dangerous. That verdict is from its built-in patterns. I gave it a graph; it gave me the exit."

### 18 — What's behind the scan  *(credibility.png)*
Quick credibility beat: 639 vectors, 11 categories, 100% OWASP LLM Top-10 — but the differentiator is composition reasoning. Don't dwell; 30 seconds.

### 19 — What to do about it
The fix is **not** "remove a tool" — each is justified. Break the *graph*: **taint/trust tracking** (tainted data can't reach an external sink without review), a **trifecta gate** (no single agent holds all three legs — split into differently-privileged agents), **recipient binding** (send to the authenticated requester, not a model-chosen address), and **re-scan in CI** (`ziran ci` fails the build when a new tool completes a trifecta). Composition is a reviewable artifact — treat it like one.

### 20 — Close
**Say:** "If you're building, reviewing, or signing off on agents: stop asking only whether each tool is safe. Ask what they're capable of together — and put that question in your pipeline, not in an attacker's hands." Restate the thesis: *the vulnerability lives in the graph, not in any node.*

### 21 — Resources & disclaimer
Links: `github.com/taoq-ai/quanta` (the demo agent — **education only, intentionally composable**), `github.com/taoq-ai/ziran` (the finder). Note Quanta is deliberately vulnerable by design; don't deploy it for real. Take Q&A.

---

## Demo runbook (rehearse this)

**Pre-flight (before you walk on):**
1. `pip install -e '.[data,dev]'` and `quanta-load-data` (real UCI data; `--synthetic` if no network).
2. `agentcore launch` done earlier; confirm `./scripts/invoke_demo.sh` returns an answer.
3. Pre-generate the frozen report: `QUANTA_STUB=1 PYTHONPATH=. python scripts/scan_quanta.py --out reports`; open it once to warm it.
4. Have `talk/assets/ziran_report_dashboard.png` and `reports/quanta_scan_report.html` open in background tabs.

**On stage:**
- Slide 11: `agentcore invoke '{"prompt":"Revenue by country, top 5"}'` (live, real AWS).
- Slide 17: `QUANTA_STUB=1 PYTHONPATH=. python scripts/scan_quanta.py` then `open reports/*.html`.
- **If wifi/AWS fails:** skip the live invoke, narrate over the dashboard screenshot. The scan runs in-process and offline, so it almost never needs the network — but the frozen HTML is the ultimate safety net.

**Timing guardrails:** if running long, cut slide 7 and shorten 18. Never cut the reveal (16–17).
