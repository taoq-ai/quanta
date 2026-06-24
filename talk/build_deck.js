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
  s.addNotes(
    "SAY: 'By the end, you'll have watched a clean, well-built agent get one critical finding — and it isn't in any of its tools.'\n" +
    "· Land the title. Pause. Let it sit.\n" +
    "· 45 min — about 30 talk, 10 demo, 5 Q&A.");
}

// 2 — cold open
{
  const s = p.addSlide();
  darkTitle(s, "The part everyone is already looking at", "Everyone watches the prompt.",
    "Jailbreaks, injection, guardrails — real, and well-guarded. I want the risk nobody's looking at, because it isn't visible from where they're standing.");
  s.addNotes(
    "SAY: 'Everyone watches the prompt — jailbreaks, injection, guardrails. That's real, and it's well guarded.'\n" +
    "· Then: 'I want the risk nobody's looking at — because you can't see it from there.'\n" +
    "→ so where do you look instead?");
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
  s.addNotes(
    "SAY: 'A review sees a list of tools. An agent sees a graph.'\n" +
    "· A review checks each tool on its own — like endpoints on a form.\n" +
    "· But an agent calls one tool, then feeds its output into the next.\n" +
    "· That's a graph: what it can do NEXT.\n" +
    "· The whole talk turns on this. One tool at a time, the dangerous combo is invisible.");
}

// 4 — section 1
{ const s = p.addSlide(); section(s, "1", "How an attacker navigates an agent", "Forget the model for a minute. Think like someone who just got access."); s.addNotes("SAY: 'Forget the model for a minute. Think like someone who just got access to the agent.'"); }

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
  s.addNotes(
    "SAY: 'An attacker doesn't hunt for one bad tool. They hunt for a path.'\n" +
    "· Recon — what tools are here?\n" +
    "· Mapping — what does each one touch? Data, network, code?\n" +
    "· Chaining — which order turns safe steps into one bad outcome?\n" +
    "· That's walking the graph by hand. Ziran does it automatically.");
}

// 6 — lethal trifecta
imageSlide("The lethal trifecta", "lethal-trifecta.png", 1000, 660,
  "Private data + untrusted content + external comms in one agent. (Framing: Simon Willison.)",
  "SAY: 'Three powers, each fine on its own, deadly together.'\n" +
  "· Private data. Untrusted content. The ability to send out.\n" +
  "· Any agent with all three can be steered to read secrets and send them — all through allowed actions.\n" +
  "· The name is Simon Willison's: the lethal trifecta.");

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
  s.addNotes(
    "SAY: 'Same shape, two outcomes.'\n" +
    "· Exfiltration: read private, then send out.\n" +
    "· RCE: fetch untrusted, run code, reach the network.\n" +
    "· Neither is a bug in one tool. Both live in the graph.\n" +
    "· We'll focus on exfiltration — the more relatable one.");
}

// 8 — why reviews miss it
imageSlide("Why most reviews can't catch it", "review-blindness.png", 1100, 560,
  "Tool-by-tool, everything passes. The composition stays invisible — until someone connects the dots.",
  "SAY: 'Tool by tool, everything passes. The dangerous combination stays invisible.'\n" +
  "· A review looks one endpoint at a time — and from there, the path can't be seen.\n" +
  "· 'It stays invisible until someone connects the dots. The only question is whether that someone works for you.'");

// 9 — section 2
{ const s = p.addSlide(); section(s, "2", "Meet the target", "An agent I built. Try to find the problem while I describe it."); s.addNotes("SAY: 'Let me show you an agent I built — and try to spot the problem while I describe it.'"); }

// 10 — C4 solution design
imageSlide("Quanta — the solution design (C4)", "c4-container.png", 1180, 800,
  "Analyst → AgentCore runtime (Strands + Claude) → four tools → read-only replica, allowlisted (untrusted) reference, audited mail.",
  "SAY: 'This is the design. A normal, sensible architecture.'\n" +
  "· The analyst talks to the agent; it sequences four tools.\n" +
  "· They reach a read-only database, outside reference sources, and an audited mail relay.\n" +
  "· Point at the tags along the bottom: PRIVATE in, UNTRUSTED in, EXTERNAL out — all three in one agent.\n" +
  "· 'Nothing here looks wrong yet.'");

// 11 — quanta architecture (controls)
imageSlide("…and notice it's well-built", "architecture.png", 1100, 660,
  "Hexagonal. Read-only replica, parameterised queries, sandboxed compute, egress allowlist, audited delivery. This passes review.",
  "SAY: 'And notice — it's well built. Every box here is something you'd sign off on.'\n" +
  "· Read-only database, no raw SQL, sandboxed compute with no network, an allowlist on outbound fetches, audited mail.\n" +
  "· 'This is not a toy. No open eval, no raw SQL, no open egress.'");

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
    "*** LIVE DEMO — Part 1: it's a real agent ***\n\n" +
    "Run:  python scripts/demo.py --pause        (whole demo: ask -> scan -> exploit)\n" +
    "  just this part:           ask\n" +
    "  real Bedrock, no deploy:  ask --online\n" +
    "  the deployed agent:       ask --cloud\n\n" +
    "· Three real questions: revenue by country, orders per country, top customers.\n" +
    "· Real numbers from the public UCI retail dataset.\n" +
    "SAY: 'Real agent, real data, genuinely useful. Now — is it safe?'");
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
  s.addNotes(
    "SAY: 'Four tools. Each with a real control.'\n" +
    "· search_database — read-only, no raw SQL.\n" +
    "· run_analysis — sandboxed, no network.\n" +
    "· fetch_reference — egress allowlist.\n" +
    "· send_email_report — domain allowlist, audit, dry-run.\n" +
    "· 'Reviewed one at a time, it's 4 out of 4 approved. Hold that thought.'");
}

// 14 — section 3
{ const s = p.addSlide(); section(s, "3", "Live — find the composition", "Stop reviewing tools one at a time. Look at what they do together."); s.addNotes("SAY: 'Instead of reviewing tools one at a time, let's look at what they can do together.'"); }

// 15 — meet Ziran (intro)
{
  const s = p.addSlide();
  contentHead(s, "Meet Ziran");
  s.addShape(p.ShapeType.roundRect, { x: 0.7, y: 1.55, w: 11.93, h: 0.95, fill: { color: INDIGOL }, line: { color: INDIGO, width: 1 }, rectRadius: 0.1 });
  s.addText("An open-source scanner for what an agent's tools can do together — not whether each one is safe alone.",
    { x: 1.05, y: 1.55, w: 11.2, h: 0.95, valign: "middle", fontFace: HEAD, fontSize: 19, color: INDIGO, bold: true, lineSpacingMultiple: 1.05 });
  const items = [
    ["Static analysis", "Reads the agent's tool graph — it doesn't need to run the live model."],
    ["Known-dangerous compositions", "Looks for structural patterns like the lethal trifecta, not keywords."],
    ["Local or in CI", "A check you can put in your pipeline, before anyone is attacked."],
    ["Complements red-teaming", "Finds the path that exists; red-teaming tests whether a given model walks it."],
  ];
  let y = 2.75;
  items.forEach(([h, d]) => {
    s.addShape(p.ShapeType.ellipse, { x: 0.9, y: y + 0.16, w: 0.28, h: 0.28, fill: { color: INDIGO } });
    s.addText(h, { x: 1.45, y, w: 4.5, h: 0.78, valign: "middle", fontFace: HEAD, fontSize: 17, color: INK, bold: true });
    s.addText(d, { x: 6.05, y, w: 6.5, h: 0.78, valign: "middle", fontFace: BODY, fontSize: 14.5, color: SLATE, lineSpacingMultiple: 1.05 });
    y += 0.9;
  });
  s.addText("Open source · github.com/taoq-ai/ziran", { x: 0.7, y: 6.4, w: 11.9, h: 0.4, fontFace: "Courier New", fontSize: 13, color: MUTE });
  s.addNotes(
    "SAY: 'Quick intro — what Ziran actually is.'\n" +
    "· An open-source scanner that looks at what an agent's tools can do together.\n" +
    "· Static — it reads the tool graph, doesn't need to run the model.\n" +
    "· It looks for known-dangerous combinations, like the trifecta.\n" +
    "· Runs locally or in CI — and it complements prompt red-teaming, doesn't replace it.\n" +
    "· Keep it light — the next slide is how it works.");
}

// 16 — what ziran does
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
  s.addNotes(
    "SAY: 'Ziran builds the agent's capability graph — every tool, and every way one tool's output can flow into another.'\n" +
    "· Then it checks that graph for known-dangerous combinations: direct, indirect, and loops.\n" +
    "· 'It's not testing prompts here. It's reasoning about structure.'");
}

// 17 — graph evolution
imageSlide("The graph, in three steps", "graph-evolution.png", 1200, 460,
  "Four approved tools → the agent can sequence them → one path is an exit.",
  "SAY (walk the three panels): 'Four approved tools → the agent can sequence them → one path is an exit.'\n" +
  "· 'Nothing here is hypothetical. An agent really can call send right after search.'");

// 18 — the reveal
imageSlide("…and the composition is still critical", "architecture-overlay.png", 1100, 660,
  "Every control held. The path between them did not — and the agent can walk it.",
  "SAY slowly: 'Every control still holds. Read-only: held. Sandbox: held. Allowlists: held.'\n" +
  "· 'And here's the path: untrusted content comes in, the agent reads private data, and ships it out — every step allowed.'\n" +
  "· 'Every box was hardened. The arrow wasn't.'");

// 19 — the real interactive graph (animated GIF)
imageSlide("This isn't a drawing — it's the scan", "ziran_graph.gif", 940, 825,
  "The red node IS the finding: Ziran flags the composition statically, then confirms the live exfil dynamically.",
  "*** LIVE DEMO — find the composition ***\n\n" +
  "Run:  python scripts/demo.py scan        (installs local Ziran if needed, opens the report)\n\n" +
  "· It scans in-process and prints two beats:\n" +
  "   STATIC  — the dangerous path Ziran finds in the tool graph.\n" +
  "   DYNAMIC — Ziran confirms the real leak from the actual tool calls.\n" +
  "· Then it opens the report. Pan the graph, click the red node.\n" +
  "· (The slide has the real graph as a looping GIF — the fallback if the live open stalls.)\n\n" +
  "SAY (static): 'I didn't tell Ziran this was dangerous. I gave it a graph; it handed me the exit.'\n" +
  "SAY (dynamic): 'And it's not theoretical — it confirms the leak from the real tool calls. Notice what it does NOT flag: an agent just listing its tools. The finding is the composition, not a keyword.'");

// 20 — section 4
{ const s = p.addSlide(); section(s, "4", "From finding to breach — and back", "Ziran found the path. Now watch an attacker walk it — then watch us close it."); s.addNotes("SAY: 'Ziran found the path before anyone attacked. Now let's walk it like an attacker — then close it.'"); }

// 21 — exploit, live
imageSlide("Theoretical? Watch it happen — live, offline", "exploit_vulnerable.png", 1287, 368,
  "Benign request + a poisoned reference → the full customer table (names + emails) to an attacker mailbox on the ALLOWLISTED domain. Every per-tool control held.",
  "*** LIVE DEMO — the breach ***\n\n" +
  "Run:  python scripts/demo.py exploit --vulnerable-only   (offline, deterministic)\n\n" +
  "Walk the table:\n" +
  "· A benign request → fetch_reference returns an allowlisted page with a hidden instruction (injection, LLM01).\n" +
  "· The agent obeys → search_database reads the customer table (names + emails).\n" +
  "· Watch the taint go red: PRIVATE + UNTRUSTED — the trifecta, in one run.\n" +
  "· send_email_report ships the whole customer list to an attacker mailbox ON the allowlisted domain — the check passed.\n" +
  "· The model picked the recipient = excessive agency (LLM06).\n\n" +
  "SAY slowly: 'No control was bypassed. The data left through fully allowed actions.'");

// 22 — three vulnerabilities, one agent
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
  s.addNotes(
    "SAY: 'Name what we just saw — one harmless-looking agent, three problems stacked.'\n" +
    "· The composition — structural. Ziran finds it before any attack.\n" +
    "· The injection — the trigger (LLM01).\n" +
    "· The model-chosen recipient — the missing control (LLM06).\n" +
    "· None of them is a bug in a single tool.");
}

// 23 — hardened, live
imageSlide("Break the graph: the same attack, blocked", "exploit_hardened.png", 1287, 343,
  "One injected security policy. Injection refused as data; model-chosen recipient denied; the analyst's summary still goes out. Same agent, same payload.",
  "*** LIVE DEMO — the fix ***\n\n" +
  "Run:  python scripts/demo.py exploit --hardened-only   (or scroll to the 2nd run)\n\n" +
  "· Same agent, same payload, opposite outcome:\n" +
  "   - injected instruction REFUSED as data (LLM01)\n" +
  "   - model-chosen recipient DENIED (LLM06)\n" +
  "   - trifecta gate stops a private+untrusted run from sending out.\n" +
  "· But the analyst's real summary STILL goes out.\n\n" +
  "SAY: 'The fix didn't break the product. We broke the path, not the agent.'");

// 24 — what actually breaks the path
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
  s.addNotes(
    "SAY: 'The fix isn't remove a tool — each one is justified. You break the graph.'\n" +
    "· No instructions from data — fetched content can't issue commands (LLM01).\n" +
    "· Recipient binding — mail only goes to the real requester (LLM06).\n" +
    "· Trifecta gate — a private+untrusted run can't send out on its own. Aggregates aren't private, so the real task still works.\n" +
    "· Re-scan in CI — fail the build when a new tool completes the trifecta.\n" +
    "· It's all real, tested code in quanta/security/.");
}

// 25 — multi-agent: the distributed trifecta
imageSlide("What about multi-agent systems?", "multi-agent-trifecta.png", 1180, 740,
  "Split into least-privileged agents and the trifecta reassembles across them — via messages and shared memory.",
  "SAY: 'The obvious question — doesn't splitting into smaller, least-privilege agents fix this?'\n" +
  "· Necessary, but not enough.\n" +
  "· Walk the red path: a poisoned doc hits the Research agent → the instruction rides shared memory to the Analytics agent (reads PII) → hands off to the Comms agent (sends out).\n" +
  "· No single agent holds all three legs — the SYSTEM does.\n" +
  "· The graph didn't shrink. It got bigger and harder to see.");

// 26 — breaking the graph across agents
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
  s.addNotes(
    "SAY: 'Same fix, one level up.'\n" +
    "· Constrain who talks to whom — not a full mesh.\n" +
    "· Carry taint across messages; enforce at agent boundaries.\n" +
    "· Quarantine the untrusted-facing agent — structured output only, never instructions to privileged agents.\n" +
    "· One gate where a private+untrusted flow could reach the outside.\n" +
    "· Re-scan the whole system graph in CI.\n" +
    "SAY (kicker): 'No single tool was dangerous — and no single agent is either. The risk lives in how they connect.'");
}

// 27 — close
{
  const s = p.addSlide();
  s.background = { color: INK };
  s.addText("The question isn't whether your\ntools are safe individually.", { x: 0.8, y: 2.1, w: 11.7, h: 1.8, fontFace: HEAD, fontSize: 40, color: WHITE, bold: true, lineSpacingMultiple: 1.05 });
  s.addText("It's what they're capable of together — and whether you ask that question before an attacker does.", { x: 0.82, y: 4.1, w: 11.2, h: 1.4, fontFace: BODY, fontSize: 22, color: "818CF8", italic: true, lineSpacingMultiple: 1.1 });
  s.addNotes(
    "SAY: 'The question isn't whether your tools are safe one by one. It's what they can do together — and whether you ask that before an attacker does.'\n" +
    "· Restate the thesis: the vulnerability lives in the graph, not in any node.");
}

// 28 — resources + disclaimer
{
  const s = p.addSlide();
  contentHead(s, "Try it yourself");
  // Quanta card (text left, QR right)
  s.addShape(p.ShapeType.roundRect, { x: 0.7, y: 1.7, w: 5.85, h: 2.3, fill: { color: INDIGOL }, line: { color: INDIGO, width: 1 }, rectRadius: 0.1 });
  s.addText([{ text: "Quanta\n", options: { bold: true, color: INDIGO, fontSize: 20, fontFace: HEAD } }, { text: "github.com/taoq-ai/quanta\n\n", options: { color: SLATE, fontSize: 13, fontFace: "Courier New" } }, { text: "The demo agent — defensible architecture, one composition finding.", options: { color: SLATE, fontSize: 14 } }], { x: 1.05, y: 1.95, w: 3.55, h: 1.9, valign: "top", fontFace: BODY, lineSpacingMultiple: 1.1 });
  s.addShape(p.ShapeType.roundRect, { x: 4.78, y: 1.95, w: 1.6, h: 1.6, fill: { color: WHITE }, rectRadius: 0.06 });
  s.addImage({ path: A("qr_quanta.png"), x: 4.88, y: 2.05, w: 1.4, h: 1.4 });
  s.addText("scan to open", { x: 4.78, y: 3.55, w: 1.6, h: 0.3, align: "center", fontFace: BODY, fontSize: 10, color: MUTE });
  // Ziran card (text left, QR right)
  s.addShape(p.ShapeType.roundRect, { x: 6.78, y: 1.7, w: 5.85, h: 2.3, fill: { color: "ECFDF5" }, line: { color: GREEN, width: 1 }, rectRadius: 0.1 });
  s.addText([{ text: "Ziran\n", options: { bold: true, color: GREEN, fontSize: 20, fontFace: HEAD } }, { text: "github.com/taoq-ai/ziran\n\n", options: { color: SLATE, fontSize: 13, fontFace: "Courier New" } }, { text: "Open-source — the composition analysis used here.", options: { color: SLATE, fontSize: 14 } }], { x: 7.13, y: 1.95, w: 3.55, h: 1.9, valign: "top", fontFace: BODY, lineSpacingMultiple: 1.1 });
  s.addShape(p.ShapeType.roundRect, { x: 10.86, y: 1.95, w: 1.6, h: 1.6, fill: { color: WHITE }, rectRadius: 0.06 });
  s.addImage({ path: A("qr_ziran.png"), x: 10.96, y: 2.05, w: 1.4, h: 1.4 });
  s.addText("scan to open", { x: 10.86, y: 3.55, w: 1.6, h: 0.3, align: "center", fontFace: BODY, fontSize: 10, color: MUTE });
  s.addShape(p.ShapeType.roundRect, { x: 0.7, y: 4.3, w: 11.93, h: 1.5, fill: { color: REDL }, line: { color: RED, width: 1.2 }, rectRadius: 0.1 });
  s.addText([{ text: "⚠  Education only.  ", options: { bold: true, color: RED } }, { text: "Quanta is deliberately composable and has a known, intentional vulnerability by design. Do not deploy it for real or connect it to real data.", options: { color: "7F1D1D" } }], { x: 1.05, y: 4.3, w: 11.2, h: 1.5, valign: "middle", fontFace: BODY, fontSize: 16, lineSpacingMultiple: 1.1 });
  s.addText("Thank you — questions?", { x: 0.7, y: 6.1, w: 11.9, h: 0.8, align: "center", fontFace: HEAD, fontSize: 24, color: INK, bold: true });
  s.addNotes(
    "SAY: 'Two repos to try this yourself.' Point to the QR codes.\n" +
    "· Quanta — the demo agent. Education only, vulnerable by design. Don't deploy it for real.\n" +
    "· Ziran — open source, the composition analysis you just saw.\n" +
    "· Thank the room. Take Q&A.");
}

p.writeFile({ fileName: path.join(__dirname, "quanta-talk.pptx") }).then((f) => console.log("wrote", f));
