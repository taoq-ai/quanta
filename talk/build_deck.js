// Build the talk deck: "When Your Agent Tools Combine Against You"
// Run:  NODE_PATH=$(npm root -g) node talk/build_deck.js
// Speaker notes are embedded per slide (View > Notes / Presenter View).
const path = require("path");
const pptxgen = require("pptxgenjs");

const A = (f) => path.join(__dirname, "assets", f);
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
p.layout = "W";

// ---- palette ----
const INK = "0F172A", SLATE = "334155", MUTE = "64748B", LIGHT = "F8FAFC";
const INDIGO = "4338CA", INDIGOL = "EEF2FF", RED = "DC2626", REDL = "FEF2F2";
const GREEN = "059669", WHITE = "FFFFFF";
const HEAD = "Cambria", BODY = "Arial";

const fit = (natW, natH, box) => {
  const r = natW / natH, br = box.w / box.h;
  let w = box.w, h = box.h;
  if (r > br) { h = box.w / r; } else { w = box.h * r; }
  return { x: box.x + (box.w - w) / 2, y: box.y + (box.h - h) / 2, w, h };
};

// ---------- reusable slide types ----------
function darkTitle(s, kicker, title, sub) {
  s.background = { color: INK };
  if (kicker) s.addText(kicker.toUpperCase(), { x: 0.8, y: 1.7, w: 11.7, h: 0.5, fontFace: BODY, fontSize: 16, color: "818CF8", bold: true, charSpacing: 3 });
  s.addText(title, { x: 0.8, y: 2.2, w: 11.7, h: 2.2, fontFace: HEAD, fontSize: 46, color: WHITE, bold: true, lineSpacingMultiple: 1.02 });
  if (sub) s.addText(sub, { x: 0.82, y: 4.55, w: 11.4, h: 1.4, fontFace: BODY, fontSize: 20, color: "CBD5E1" });
}
function section(s, num, title, sub) {
  s.background = { color: INK };
  s.addShape(p.ShapeType.ellipse, { x: 0.8, y: 2.5, w: 1.2, h: 1.2, fill: { color: INDIGO } });
  s.addText(num, { x: 0.8, y: 2.5, w: 1.2, h: 1.2, align: "center", valign: "middle", fontFace: HEAD, fontSize: 34, color: WHITE, bold: true });
  s.addText(title, { x: 2.3, y: 2.55, w: 10, h: 1.2, fontFace: HEAD, fontSize: 38, color: WHITE, bold: true });
  if (sub) s.addText(sub, { x: 2.33, y: 3.75, w: 9.8, h: 0.8, fontFace: BODY, fontSize: 18, color: "94A3B8" });
}
function contentHead(s, title) {
  s.background = { color: LIGHT };
  s.addText(title, { x: 0.7, y: 0.5, w: 12, h: 0.9, fontFace: HEAD, fontSize: 32, color: INK, bold: true });
}
function imageSlide(title, img, natW, natH, caption, notes) {
  const s = p.addSlide();
  contentHead(s, title);
  const box = { x: 0.7, y: 1.55, w: 11.93, h: caption ? 5.0 : 5.4 };
  s.addImage({ path: A(img), ...fit(natW, natH, box) });
  if (caption) s.addText(caption, { x: 0.7, y: 6.7, w: 11.93, h: 0.5, align: "center", fontFace: BODY, fontSize: 15, italic: true, color: MUTE });
  if (notes) s.addNotes(notes);
  return s;
}

// =========================================================
// 1 — Title
// =========================================================
{
  const s = p.addSlide();
  s.background = { color: INK };
  s.addText("When Your Agent Tools\nCombine Against You", { x: 0.8, y: 2.0, w: 11.7, h: 2.6, fontFace: HEAD, fontSize: 52, color: WHITE, bold: true, lineSpacingMultiple: 1.03 });
  s.addText("The vulnerability lives in the graph, not in any node.", { x: 0.82, y: 4.75, w: 11, h: 0.6, fontFace: BODY, fontSize: 22, color: "818CF8", italic: true });
  s.addText("Live demo: a real Amazon Bedrock AgentCore agent, found with Ziran", { x: 0.82, y: 5.7, w: 11, h: 0.5, fontFace: BODY, fontSize: 16, color: "94A3B8" });
  s.addNotes("Land the title, then a beat. 'By the end you'll have watched a clean, well-architected agent get one critical finding — and the finding isn't in any of its tools.' Audience: builders/engineers. 45 min: ~30 talk + ~10 demo + ~5 Q&A.");
}

// 2 — cold open
{
  const s = p.addSlide();
  darkTitle(s, "The part everyone is already looking at", "Everyone watches the prompt.",
    "Jailbreaks, injection, guardrails — real, and well-guarded. I want the risk nobody's looking at, because it isn't visible from where they're standing.");
  s.addNotes("Most AI-security energy goes at the prompt: jailbreaks, injection, guardrails. It matters — but it's the part everyone is already looking at. Say: 'I want the risk nobody's looking at, because it isn't visible from where they're standing.'");
}

// 3 — tools are a graph
{
  const s = p.addSlide();
  contentHead(s, "A review sees a list. An agent has a graph.");
  s.addText([
    { text: "How reviews look at tools\n", options: { bold: true, color: INDIGO, fontSize: 18 } },
    { text: "A flat inventory — tool by tool, endpoint by endpoint. Each one checked in isolation, like API endpoints on a form.", options: { fontSize: 16, color: SLATE } },
  ], { x: 0.7, y: 1.7, w: 5.7, h: 2.4, fontFace: BODY, valign: "top", lineSpacingMultiple: 1.15 });
  s.addText([
    { text: "What an agent actually is\n", options: { bold: true, color: RED, fontSize: 18 } },
    { text: "An LLM can call any tool, then feed its output into the next. That's not a list — it's a graph of what the agent can do next.", options: { fontSize: 16, color: SLATE } },
  ], { x: 6.9, y: 1.7, w: 5.7, h: 2.4, fontFace: BODY, valign: "top", lineSpacingMultiple: 1.15 });
  s.addShape(p.ShapeType.roundRect, { x: 0.7, y: 4.5, w: 11.93, h: 1.9, fill: { color: INDIGOL }, line: { color: INDIGO, width: 1 }, rectRadius: 0.12 });
  s.addText("The whole talk turns on this: review one tool at a time and the dangerous combination is invisible — it isn't in any single tool.",
    { x: 1.1, y: 4.5, w: 11.1, h: 1.9, valign: "middle", fontFace: HEAD, fontSize: 22, color: INDIGO, bold: true, lineSpacingMultiple: 1.1 });
  s.addNotes("A security review enumerates tools like API endpoints: a list. But an LLM agent can call any tool, then feed its output into the next. That's not a list — it's a graph of what the agent can do next. Hold this idea; the whole talk turns on it.");
}

// 4 — section 1
{ const s = p.addSlide(); section(s, "1", "How an attacker navigates an agent", "Forget the model for a minute. Think like someone who just got access."); s.addNotes("Divider. 'Forget the model for a minute. Think like someone who just got access to the agent.'"); }

// 5 — attacker mental model
{
  const s = p.addSlide();
  contentHead(s, "Attackers don't hunt for a bad tool. They hunt for a path.");
  const rows = [
    ["Recon", "What tools exist? What can this agent reach?", INDIGO],
    ["Capability mapping", "What does each tool touch — private data, the network, code execution?", "7C3AED"],
    ["Chaining", "Which sequence turns reasonable actions into one bad outcome?", RED],
  ];
  let y = 1.8;
  rows.forEach(([h, d, c], i) => {
    s.addShape(p.ShapeType.ellipse, { x: 0.8, y: y + 0.1, w: 0.8, h: 0.8, fill: { color: c } });
    s.addText(String(i + 1), { x: 0.8, y: y + 0.1, w: 0.8, h: 0.8, align: "center", valign: "middle", fontFace: HEAD, fontSize: 22, color: WHITE, bold: true });
    s.addText(h, { x: 1.9, y: y, w: 4.2, h: 0.9, valign: "middle", fontFace: HEAD, fontSize: 22, color: INK, bold: true });
    s.addText(d, { x: 6.1, y: y, w: 6.5, h: 0.9, valign: "middle", fontFace: BODY, fontSize: 16, color: SLATE });
    y += 1.25;
  });
  s.addText("This is graph traversal — done by hand. Ziran does it automatically.", { x: 0.8, y: 6.2, w: 11.8, h: 0.6, fontFace: BODY, fontSize: 17, italic: true, color: MUTE });
  s.addNotes("Three moves: recon (what tools exist?), capability mapping (what does each touch — data? network? compute?), chaining (which sequence turns reasonable actions into one bad outcome?). Attackers don't look for A dangerous tool. They look for a PATH. This is graph traversal, done by hand.");
}

// 6 — lethal trifecta
imageSlide("The lethal trifecta", "lethal-trifecta.png", 1000, 660,
  "Private data + untrusted content + external comms in one agent. (Framing: Simon Willison.)",
  "Three capabilities individually fine and collectively lethal: access to private data, exposure to untrusted content, the ability to communicate externally. Any agent with all three can be steered to read secrets and send them out — through entirely authorised actions. Credit Simon Willison's 'lethal trifecta'.");

// 7 — two failure shapes
{
  const s = p.addSlide();
  contentHead(s, "Same structure, two failure shapes");
  const card = (x, title, parts, tint, line) => {
    s.addShape(p.ShapeType.roundRect, { x, y: 1.7, w: 5.85, h: 4.6, fill: { color: tint }, line: { color: line, width: 1.2 }, rectRadius: 0.12 });
    s.addText(title, { x: x + 0.4, y: 2.0, w: 5.05, h: 0.6, fontFace: HEAD, fontSize: 22, color: line, bold: true });
    s.addText(parts, { x: x + 0.4, y: 2.7, w: 5.05, h: 3.4, fontFace: BODY, fontSize: 17, color: SLATE, valign: "top", lineSpacingMultiple: 1.2 });
  };
  card(0.7, "Data exfiltration", [
    { text: "read private data", options: { bold: true, color: INK } },
    { text: "  →  ", options: { color: RED, bold: true } },
    { text: "send externally\n\n", options: { bold: true, color: INK } },
    { text: "A read tool + a send tool isn't two features. It's an exit, waiting for the right prompt.", options: {} },
  ], REDL, RED);
  card(6.78, "Remote code execution", [
    { text: "fetch untrusted", options: { bold: true, color: INK } },
    { text: "  →  ", options: { color: "B45309", bold: true } },
    { text: "execute", options: { bold: true, color: INK } },
    { text: "  +  network\n\n", options: { color: "B45309", bold: true } },
    { text: "Search + code execution + network access isn't three productivity features. It's an RCE surface.", options: {} },
  ], "FFF7ED", "B45309");
  s.addText("Neither is a bug in a node. Both are properties of the graph.", { x: 0.7, y: 6.55, w: 11.9, h: 0.5, align: "center", fontFace: HEAD, fontSize: 18, color: INK, bold: true });
  s.addNotes("Same structural idea, two shapes. Exfiltration: read + send. RCE surface: fetch untrusted + execute + network. Neither is a bug in a node. Both are properties of the graph. (Our demo focuses on exfiltration — the subtler, more relatable one.)");
}

// 8 — why reviews miss it
imageSlide("Why most reviews can't catch it", "review-blindness.png", 1100, 560,
  "Tool-by-tool, everything passes. The composition stays invisible — until someone connects the dots.",
  "Reviews look tool-by-tool, endpoint-by-endpoint — and tool-by-tool, everything passes. The composition is invisible from that vantage point. Say: 'It stays invisible until someone connects the dots. The only question is whether that someone works for you.'");

// 9 — section 2
{ const s = p.addSlide(); section(s, "2", "Meet the target", "An agent I built. Try to find the problem while I describe it."); s.addNotes("Divider. 'Let me show you an agent I built — and I want you to try to find the problem while I describe it.'"); }

// 10 — C4 solution design
imageSlide("Quanta — the solution design (C4)", "c4-container.png", 1180, 800,
  "Analyst → AgentCore runtime (Strands + Claude) → four tools → read-only replica, allowlisted (untrusted) reference, audited mail.",
  "Solution design, C4 container view. A real, sensible architecture: the analyst talks to the Quanta AgentCore runtime; a Strands agent backed by Bedrock Claude sequences four tool containers; those reach a read-only analytics replica, allowlisted external reference sources, and an audited mail relay. Point at the trust tags along the bottom: PRIVATE data in, UNTRUSTED content in, EXTERNAL send out — all three legs present in one runtime. Nothing here looks wrong yet.");

// 11 — quanta architecture (controls)
imageSlide("…and notice it's well-built", "architecture.png", 1100, 660,
  "Hexagonal. Read-only replica, parameterised queries, sandboxed compute, egress allowlist, audited delivery. This passes review.",
  "Zoom into the controls. Hexagonal, ports & adapters. Read-only replica, parameterised queries (no raw SQL), a sandboxed interpreter with no network, an egress allowlist on outbound fetches, audited report delivery. Say: 'This is not a toy. Every box here is something you'd sign off on. No unsandboxed eval, no raw SQL, no open egress.'");

// 12 — quanta live
{
  const s = p.addSlide();
  contentHead(s, "Quanta, live — a real, useful assistant");
  s.addShape(p.ShapeType.roundRect, { x: 0.7, y: 1.6, w: 11.93, h: 3.2, fill: { color: "0B1220" }, rectRadius: 0.08 });
  s.addText([
    { text: "$ ", options: { color: "22D3EE" } },
    { text: "agentcore invoke '{\"prompt\": \"Revenue by country, top 5\"}'\n\n", options: { color: "E2E8F0" } },
    { text: "Revenue by country\n", options: { color: "94A3B8" } },
    { text: "United Kingdom   76,654.21\nGermany          18,484.30\nFrance           15,259.32\nEIRE             12,108.35\nSpain             7,784.88", options: { color: "A7F3D0" } },
  ], { x: 1.1, y: 1.9, w: 11.1, h: 2.6, fontFace: "Courier New", fontSize: 16, valign: "top", lineSpacingMultiple: 1.1 });
  s.addText("Deployed on Amazon Bedrock AgentCore. Real numbers from the public UCI Online Retail II dataset.",
    { x: 0.7, y: 5.1, w: 11.9, h: 0.6, fontFace: BODY, fontSize: 17, color: SLATE });
  s.addText("Real agent, real data, genuinely useful. Now — is it safe?",
    { x: 0.7, y: 5.8, w: 11.9, h: 0.7, fontFace: HEAD, fontSize: 22, color: INK, bold: true });
  s.addNotes(
    "*** LIVE DEMO — Part 1: it's a real agent ***\n" +
    "Run:  python scripts/demo.py --pause          (whole demo: ask -> scan -> exploit)\n" +
    "  or just this part:  python scripts/demo.py ask              (offline stub)\n" +
    "  on the deployed agent:  python scripts/demo.py ask --cloud  (real AgentCore)\n" +
    "It asks three real questions (revenue by country top 5 / orders per country / top customers).\n" +
    "Real numbers from UCI Online Retail II. Then say: 'Real agent, real data, genuinely useful. Now — is it safe?'");
}

// 13 — four tools four controls
{
  const s = p.addSlide();
  contentHead(s, "Four tools. Four real controls.");
  const header = ["Tool", "What it does", "Its control"];
  const data = [
    ["search_database", "reads business metrics", "read-only replica · parameterised (no raw SQL)"],
    ["run_analysis", "summarises results", "sandbox · no network · no imports"],
    ["fetch_reference", "pulls external benchmarks", "egress allowlist (destination)"],
    ["send_email_report", "shares the report", "domain allowlist · audit log · dry-run"],
  ];
  const rows = [
    header.map((t) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: INDIGO }, fontSize: 15, valign: "middle" } })),
    ...data.map((r) => r.map((t, i) => ({
      text: t,
      options: { color: i === 0 ? INDIGO : SLATE, bold: i === 0, fontFace: i === 0 ? "Courier New" : BODY, fontSize: 14.5, valign: "middle", fill: { color: WHITE } },
    }))),
  ];
  s.addTable(rows, { x: 0.7, y: 1.65, w: 11.93, colW: [3.0, 3.6, 5.33], rowH: [0.5, 0.78, 0.78, 0.78, 0.78], border: { type: "solid", color: "E2E8F0", pt: 1 }, fontFace: BODY });
  s.addShape(p.ShapeType.roundRect, { x: 0.7, y: 6.35, w: 11.93, h: 0.85, fill: { color: "ECFDF5" }, line: { color: GREEN, width: 1 }, rectRadius: 0.1 });
  s.addText("A tool-by-tool review signs off — 4 / 4 approved. Hold that thought.",
    { x: 1.0, y: 6.35, w: 11.3, h: 0.85, valign: "middle", fontFace: HEAD, fontSize: 19, color: "065F46", bold: true });
  s.addNotes("Four tools. Four real controls: search_database (read-only, parameterised), run_analysis (sandboxed), fetch_reference (allowlist), send_email_report (allowlist + audit + dry-run). A tool-by-tool review signs off 4 out of 4. Hold that thought.");
}

// 14 — section 3
{ const s = p.addSlide(); section(s, "3", "Live — find the composition", "Stop reviewing tools one at a time. Look at what they do together."); s.addNotes("Divider. 'Instead of reviewing tools one at a time, let's look at what they can do together.'"); }

// 15 — what ziran does
{
  const s = p.addSlide();
  contentHead(s, "What Ziran does");
  s.addText([
    { text: "It builds the agent's capability graph", options: { bold: true, color: INK, fontSize: 19 } },
    { text: "  — every tool, and every way one tool's output can flow into another.\n\n", options: { color: SLATE, fontSize: 17 } },
    { text: "Then it checks that graph against a library of known dangerous compositions:\n", options: { color: SLATE, fontSize: 17 } },
  ], { x: 0.7, y: 1.7, w: 11.9, h: 2.0, fontFace: BODY, valign: "top", lineSpacingMultiple: 1.2 });
  const chips = [["direct", "A → B"], ["indirect", "A → … → B"], ["cycle", "A → B → … → A"]];
  chips.forEach(([h, d], i) => {
    const x = 0.7 + i * 4.05;
    s.addShape(p.ShapeType.roundRect, { x, y: 3.7, w: 3.7, h: 1.5, fill: { color: INDIGOL }, line: { color: INDIGO, width: 1.2 }, rectRadius: 0.12 });
    s.addText(h, { x, y: 3.9, w: 3.7, h: 0.6, align: "center", fontFace: HEAD, fontSize: 22, color: INDIGO, bold: true });
    s.addText(d, { x, y: 4.5, w: 3.7, h: 0.6, align: "center", fontFace: "Courier New", fontSize: 18, color: SLATE });
  });
  s.addText("Here it isn't testing prompts. It's reasoning about structure.", { x: 0.7, y: 5.7, w: 11.9, h: 0.6, fontFace: BODY, fontSize: 18, italic: true, color: MUTE });
  s.addNotes("Ziran builds the agent's capability graph and checks it against a library of known dangerous compositions — direct (A→B), indirect (A→…→B), and cycles. Say: 'It's not testing prompts here. It's reasoning about structure.'");
}

// 16 — graph evolution
imageSlide("The graph, in three steps", "graph-evolution.png", 1200, 460,
  "Four approved tools → the agent can sequence them → one path is an exit.",
  "Walk the three panels: four approved tools → the agent can sequence them (edges) → one path is an exit. Say: 'Nothing here is hypothetical. An LLM agent really can call send right after search.'");

// 17 — the reveal
imageSlide("…and the composition is still critical", "architecture-overlay.png", 1100, 660,
  "Every control held. The path between them did not — and the agent can walk it.",
  "Back to the architecture — now with the red path. Say slowly: 'Every control still holds. Read-only: held. Sandbox: held. Allowlists: held. And here's the path: untrusted content comes in through fetch_reference, the agent reads private data with search_database, and ships it out through send_email_report — every step authorised. Every box was hardened. The arrow wasn't.'");

// 18 — the real interactive graph (animated GIF)
imageSlide("This isn't a drawing — it's the scan", "ziran_graph.gif", 940, 825,
  "The real Ziran interactive graph. One critical finding: search_database → send_email_report, data_exfiltration.",
  "*** LIVE DEMO — find the composition ***\n" +
  "Run:  python scripts/demo.py scan   (installs Ziran if needed, then opens the report)\n" +
  "It scans in-process and opens reports/*_report.html — pan the graph, click the red node.\n" +
  "(This slide embeds the real interactive graph as a looping GIF — it plays in Presenter/slideshow, and is the fallback if the live open stalls.)\n" +
  "One critical finding: search_database → send_email_report, data_exfiltration. Say: 'I didn't tell Ziran this was dangerous — that verdict is from its built-in patterns. I gave it a graph; it gave me the exit. But a finding on a slide is easy to wave away — so let me show you the exit actually being used.'");

// 19 — section 4
{ const s = p.addSlide(); section(s, "4", "From finding to breach — and back", "Ziran found the path. Now watch an attacker walk it — then watch us close it."); s.addNotes("Divider. 'Ziran found the path statically, before anyone attacked. Now let's walk it like an attacker — then close it.'"); }

// 20 — exploit, live
imageSlide("Theoretical? Watch it happen — live, offline", "exploit_vulnerable.png", 1287, 368,
  "Benign request + a poisoned reference → 16,741 bytes of customer PII to an attacker mailbox on the ALLOWLISTED domain. Every per-tool control held.",
  "*** LIVE DEMO — the breach ***\n" +
  "Run:  python scripts/demo.py exploit            (offline, deterministic — prints both runs)\n" +
  "Walk the table: a benign request → fetch_reference returns an allowlisted page whose CONTENT carries a hidden instruction (indirect prompt injection, LLM01). The agent obeys → search_database reads 900 customer-level rows → watch the taint go red: PRIVATE+UNTRUSTED, the lethal trifecta in one run → send_email_report ships 16,741 bytes of PII to ops-archive@reports.acme-analytics.example. That mailbox is on the ALLOWLISTED domain — the domain check PASSED. Model-chosen recipient = excessive agency / confused deputy (LLM06). Say slowly: 'No control was bypassed. The data left through fully authorised actions.'");

// 21 — three vulnerabilities, one agent
{
  const s = p.addSlide();
  contentHead(s, "Three vulnerabilities, one agent");
  const header = ["Vulnerability", "OWASP", "Where it lives", "Caught by"];
  const data = [
    ["Tool-composition exfiltration", "structural", "search_database → send_email_report", "Ziran — static, pre-attack"],
    ["Indirect prompt injection", "LLM01", "fetched content from fetch_reference, obeyed as an instruction", "runtime policy"],
    ["Excessive agency / confused deputy", "LLM06 / 08", "send_email_report trusts a model-chosen recipient", "runtime policy"],
  ];
  const rows = [
    header.map((t) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: INDIGO }, fontSize: 14, valign: "middle" } })),
    ...data.map((r) => r.map((t, i) => ({
      text: t,
      options: { color: i === 0 ? INK : SLATE, bold: i === 0, fontSize: 13.5, valign: "middle", fill: { color: WHITE } },
    }))),
  ];
  s.addTable(rows, { x: 0.7, y: 1.65, w: 11.93, colW: [3.7, 1.4, 4.5, 2.33], rowH: [0.5, 0.95, 0.95, 0.95], border: { type: "solid", color: "E2E8F0", pt: 1 }, fontFace: BODY });
  s.addShape(p.ShapeType.roundRect, { x: 0.7, y: 5.5, w: 11.93, h: 1.4, fill: { color: REDL }, line: { color: RED, width: 1 }, rectRadius: 0.1 });
  s.addText("The composition is the precondition — Ziran finds it before anyone is attacked. The injection is the trigger; the model-chosen recipient is the missing control. All three live on four review-passing tools.",
    { x: 1.05, y: 5.5, w: 11.2, h: 1.4, valign: "middle", fontFace: HEAD, fontSize: 17, color: "7F1D1D", bold: true, lineSpacingMultiple: 1.1 });
  s.addNotes("Name what we just saw. One innocuous agent, three stacked classes: the composition (structural — Ziran finds it pre-attack), indirect prompt injection (LLM01 — the trigger), excessive agency / confused deputy (LLM06 — the missing control). None is a bug in a single tool.");
}

// 22 — hardened, live
imageSlide("Break the graph: the same attack, blocked", "exploit_hardened.png", 1287, 343,
  "One injected security policy. Injection refused as data; model-chosen recipient denied; the analyst's summary still goes out. Same agent, same payload.",
  "*** LIVE DEMO — the fix ***\n" +
  "`python scripts/demo.py exploit` already printed both runs — scroll to the second.\n" +
  "Same agent, same payload, opposite outcome: the injected instruction is REFUSED as data (LLM01); the model-chosen recipient is DENIED by recipient-binding (LLM06); the trifecta gate stops a private+untrusted run reaching an external sink. Crucially the analyst's legitimate summary STILL goes out. Say: 'The fix didn't break the product. We broke the path, not the agent.'");

// 23 — what actually breaks the path
{
  const s = p.addSlide();
  contentHead(s, "The fix isn't 'remove a tool'. Break the graph.");
  const items = [
    ["No instructions from data  ·  LLM01", "Content from fetch_reference is data, never commands — the injected step never runs."],
    ["Recipient binding  ·  LLM06", "send_email_report only reaches the authenticated requester — not a model-chosen address, even on an allowlisted domain."],
    ["Trifecta gate  ·  taint tracking", "A run holding private + untrusted data can't reach an external sink unattended. Aggregates aren't private — the real task still works."],
    ["Re-scan in CI  ·  ziran ci", "Fail the build when a newly-added tool completes a trifecta. Composition as a reviewable artifact."],
  ];
  let y = 1.65;
  items.forEach(([h, d]) => {
    s.addShape(p.ShapeType.roundRect, { x: 0.7, y, w: 11.93, h: 1.12, fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 }, rectRadius: 0.1 });
    s.addShape(p.ShapeType.ellipse, { x: 1.0, y: y + 0.31, w: 0.5, h: 0.5, fill: { color: GREEN } });
    s.addText("✓", { x: 1.0, y: y + 0.31, w: 0.5, h: 0.5, align: "center", valign: "middle", color: WHITE, fontSize: 18, bold: true });
    s.addText(h, { x: 1.75, y, w: 4.4, h: 1.12, valign: "middle", fontFace: HEAD, fontSize: 16, color: INK, bold: true });
    s.addText(d, { x: 6.2, y, w: 6.2, h: 1.12, valign: "middle", fontFace: BODY, fontSize: 14, color: SLATE, lineSpacingMultiple: 1.05 });
    y += 1.22;
  });
  s.addNotes("The fix is NOT 'remove a tool' — each is justified. Break the graph: no-instructions-from-data (LLM01), recipient binding (LLM06), trifecta gate via taint (the composition), and re-scan in CI (ziran ci fails the build when a new tool completes a trifecta). Three are runtime guardrails; the last is the design-time one that matches the thesis. It's all real, tested code in quanta/security/.");
}

// 24 — multi-agent: the distributed trifecta
imageSlide("What about multi-agent systems?", "multi-agent-trifecta.png", 1180, 740,
  "Split into least-privileged agents and the trifecta reassembles across them — via messages and shared memory.",
  "The natural question: doesn't splitting into specialised, least-privileged agents fix this? It's necessary but NOT sufficient. Walk the red path: a poisoned doc hits the Research agent (untrusted); the injected instruction rides the shared memory / message bus to the Analytics agent (reads PII), which hands off to the Comms agent (sends out). No single agent holds all three legs — the SYSTEM does. The graph didn't shrink; it got bigger and harder to see: nodes are now (agent, tool) pairs; edges are agent-to-agent messages, delegation, and shared memory. Ziran scans multi-agent topologies (router/RAG, supervisor) too.");

// 25 — breaking the graph across agents
{
  const s = p.addSlide();
  contentHead(s, "Breaking the graph — across agents");
  const maItems = [
    ["Constrain the topology", "Allowlist which agent may talk to which — not a full mesh. A private-reading agent should have no path to an external-sending one."],
    ["Provenance / taint on the bus", "Carry taint across agent-to-agent messages; enforce at agent boundaries — the trifecta gate moves up to the orchestrator."],
    ["Quarantine untrusted-facing agents", "The agent touching untrusted content emits only structured, constrained output — never free-form instructions to privileged agents (dual-LLM)."],
    ["One gate at the closure point", "A human or deterministic check where a private + untrusted flow could reach an external sink."],
    ["Re-scan the whole system graph", "A new sub-agent or inter-agent edge can complete a cross-agent trifecta — Ziran in CI fails that build."],
  ];
  let my = 1.5;
  maItems.forEach(([h, d]) => {
    s.addShape(p.ShapeType.roundRect, { x: 0.7, y: my, w: 11.93, h: 0.86, fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 }, rectRadius: 0.1 });
    s.addShape(p.ShapeType.ellipse, { x: 1.0, y: my + 0.2, w: 0.46, h: 0.46, fill: { color: GREEN } });
    s.addText("✓", { x: 1.0, y: my + 0.2, w: 0.46, h: 0.46, align: "center", valign: "middle", color: WHITE, fontSize: 17, bold: true });
    s.addText(h, { x: 1.7, y: my, w: 4.3, h: 0.86, valign: "middle", fontFace: HEAD, fontSize: 15.5, color: INK, bold: true });
    s.addText(d, { x: 6.1, y: my, w: 6.3, h: 0.86, valign: "middle", fontFace: BODY, fontSize: 13.5, color: SLATE, lineSpacingMultiple: 1.03 });
    my += 0.95;
  });
  s.addShape(p.ShapeType.roundRect, { x: 0.7, y: 6.26, w: 11.93, h: 0.66, fill: { color: INDIGOL }, line: { color: INDIGO, width: 1 }, rectRadius: 0.1 });
  s.addText("The same lesson, one level up: no single tool was dangerous — and no single agent is either. The risk lives in how they connect.",
    { x: 0.9, y: 6.26, w: 11.5, h: 0.66, valign: "middle", align: "center", fontFace: HEAD, fontSize: 15, color: INDIGO, bold: true });
  s.addNotes("This is the remediation, lifted to the system level. Constrain the topology (allowlist agent-to-agent edges — not a mesh). Carry taint/provenance across the message bus and enforce at boundaries — the trifecta gate moves up to the orchestrator. Quarantine the untrusted-facing agent (dual-LLM: structured output only, never instructions to privileged agents). One human/deterministic gate at the closure point. Re-scan the whole system graph in CI. Land the kicker: no single tool was dangerous, and no single agent is either — the risk lives in how they connect.");
}

// 26 — close
{
  const s = p.addSlide();
  s.background = { color: INK };
  s.addText("The question isn't whether your\ntools are safe individually.", { x: 0.8, y: 2.1, w: 11.7, h: 1.8, fontFace: HEAD, fontSize: 40, color: WHITE, bold: true, lineSpacingMultiple: 1.05 });
  s.addText("It's what they're capable of together — and whether you ask that question before an attacker does.", { x: 0.82, y: 4.1, w: 11.2, h: 1.4, fontFace: BODY, fontSize: 22, color: "818CF8", italic: true, lineSpacingMultiple: 1.1 });
  s.addNotes("Say: 'If you're building, reviewing, or signing off on agents: stop asking only whether each tool is safe. Ask what they're capable of together — and put that question in your pipeline, not in an attacker's hands.' Restate the thesis: the vulnerability lives in the graph, not in any node.");
}

// 27 — resources + disclaimer
{
  const s = p.addSlide();
  contentHead(s, "Try it yourself");
  s.addShape(p.ShapeType.roundRect, { x: 0.7, y: 1.7, w: 5.85, h: 2.3, fill: { color: INDIGOL }, line: { color: INDIGO, width: 1 }, rectRadius: 0.1 });
  s.addText([{ text: "Quanta\n", options: { bold: true, color: INDIGO, fontSize: 20, fontFace: HEAD } }, { text: "github.com/taoq-ai/quanta\n\n", options: { color: SLATE, fontSize: 15, fontFace: "Courier New" } }, { text: "The demo agent — defensible architecture, one composition finding. Run python scripts/demo.py yourself.", options: { color: SLATE, fontSize: 15 } }], { x: 1.05, y: 1.95, w: 5.2, h: 1.8, valign: "top", fontFace: BODY, lineSpacingMultiple: 1.1 });
  s.addShape(p.ShapeType.roundRect, { x: 6.78, y: 1.7, w: 5.85, h: 2.3, fill: { color: "ECFDF5" }, line: { color: GREEN, width: 1 }, rectRadius: 0.1 });
  s.addText([{ text: "Ziran\n", options: { bold: true, color: GREEN, fontSize: 20, fontFace: HEAD } }, { text: "github.com/taoq-ai/ziran\n\n", options: { color: SLATE, fontSize: 15, fontFace: "Courier New" } }, { text: "Open-source — the composition analysis used in this demo.", options: { color: SLATE, fontSize: 15 } }], { x: 7.13, y: 1.95, w: 5.2, h: 1.8, valign: "top", fontFace: BODY, lineSpacingMultiple: 1.1 });
  s.addShape(p.ShapeType.roundRect, { x: 0.7, y: 4.3, w: 11.93, h: 1.5, fill: { color: REDL }, line: { color: RED, width: 1.2 }, rectRadius: 0.1 });
  s.addText([{ text: "⚠  Education only.  ", options: { bold: true, color: RED } }, { text: "Quanta is deliberately composable and has a known, intentional vulnerability by design. Do not deploy it for real or connect it to real data.", options: { color: "7F1D1D" } }], { x: 1.05, y: 4.3, w: 11.2, h: 1.5, valign: "middle", fontFace: BODY, fontSize: 16, lineSpacingMultiple: 1.1 });
  s.addText("Thank you — questions?", { x: 0.7, y: 6.1, w: 11.9, h: 0.8, align: "center", fontFace: HEAD, fontSize: 24, color: INK, bold: true });
  s.addNotes("Links: github.com/taoq-ai/quanta (the demo agent — education only, intentionally composable; run scripts/exploit_demo.py), github.com/taoq-ai/ziran (the finder). Note Quanta is deliberately vulnerable by design; don't deploy it for real. Take Q&A.");
}

p.writeFile({ fileName: path.join(__dirname, "quanta-talk.pptx") }).then((f) => console.log("wrote", f));
