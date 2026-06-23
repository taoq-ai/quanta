// Build the talk deck: "When Your Agent Tools Combine Against You"
// Run:  NODE_PATH=$(npm root -g) node talk/build_deck.js
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
function imageSlide(title, img, natW, natH, caption) {
  const s = p.addSlide();
  contentHead(s, title);
  const box = { x: 0.7, y: 1.55, w: 11.93, h: caption ? 5.0 : 5.4 };
  s.addImage({ path: A(img), ...fit(natW, natH, box) });
  if (caption) s.addText(caption, { x: 0.7, y: 6.7, w: 11.93, h: 0.5, align: "center", fontFace: BODY, fontSize: 15, italic: true, color: MUTE });
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
  s.addText("Live demo: a real Amazon Bedrock AgentCore agent, found with ZIRAN", { x: 0.82, y: 5.7, w: 11, h: 0.5, fontFace: BODY, fontSize: 16, color: "94A3B8" });
}

// 2 — cold open
{
  const s = p.addSlide();
  darkTitle(s, "The part everyone is already looking at", "Everyone watches the prompt.",
    "Jailbreaks, injection, guardrails — real, and well-guarded. I want the risk nobody's looking at, because it isn't visible from where they're standing.");
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
}

// 4 — section 1
{ const s = p.addSlide(); section(s, "1", "How an attacker navigates an agent", "Forget the model for a minute. Think like someone who just got access."); }

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
  s.addText("This is graph traversal — done by hand. ZIRAN does it automatically.", { x: 0.8, y: 6.2, w: 11.8, h: 0.6, fontFace: BODY, fontSize: 17, italic: true, color: MUTE });
}

// 6 — lethal trifecta
imageSlide("The lethal trifecta", "lethal-trifecta.png", 1000, 620,
  "Private data + untrusted content + external comms in one agent. (Framing: Simon Willison.)");

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
}

// 8 — why reviews miss it
imageSlide("Why most reviews can't catch it", "review-blindness.png", 1100, 560,
  "Tool-by-tool, everything passes. The composition stays invisible — until someone connects the dots.");

// 9 — section 2
{ const s = p.addSlide(); section(s, "2", "Meet the target", "An agent I built. Try to find the problem while I describe it."); }

// 10 — quanta architecture
imageSlide("Quanta — and notice it's well-built", "architecture.png", 1100, 660,
  "Hexagonal. Read-only replica, parameterised queries, sandboxed compute, egress allowlist, audited delivery. This passes review.");

// 11 — quanta live
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
}

// 12 — four tools four controls
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
}

// 13 — section 3
{ const s = p.addSlide(); section(s, "3", "Live — find the composition", "Stop reviewing tools one at a time. Look at what they do together."); }

// 14 — what ziran does
{
  const s = p.addSlide();
  contentHead(s, "What ZIRAN does differently");
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
}

// 15 — graph evolution
imageSlide("The graph, in three steps", "graph-evolution.png", 1200, 460,
  "Four approved tools → the agent can sequence them → one path is an exit.");

// 16 — the reveal
imageSlide("…and the composition is still critical", "architecture-overlay.png", 1100, 660,
  "Every control held. The path between them did not — and the agent can walk it.");

// 17 — the real report
imageSlide("This isn't a drawing — it's the scan", "ziran_report_dashboard.png", 1440, 1024,
  "One critical finding: search_database → send_email_report, data_exfiltration. I never labelled it — ZIRAN's built-in patterns did.");

// 18 — credibility
imageSlide("What's behind the scan", "credibility.png", 1100, 560, null);

// 19 — what to do
{
  const s = p.addSlide();
  contentHead(s, "The fix isn't 'remove a tool'. Break the graph.");
  const items = [
    ["Taint / trust tracking", "Tainted data (private reads, untrusted content) can't reach an external sink without review."],
    ["Trifecta gate", "No single agent holds all three legs. Split into separate, differently-privileged agents."],
    ["Recipient binding", "Send to the authenticated requester — not a model-chosen address, even an allowlisted one."],
    ["Re-scan in CI", "ziran ci fails the build when a newly-added tool completes a trifecta."],
  ];
  let y = 1.7;
  items.forEach(([h, d]) => {
    s.addShape(p.ShapeType.roundRect, { x: 0.7, y, w: 11.93, h: 1.12, fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 }, rectRadius: 0.1 });
    s.addShape(p.ShapeType.ellipse, { x: 1.0, y: y + 0.31, w: 0.5, h: 0.5, fill: { color: INDIGO } });
    s.addText("✓", { x: 1.0, y: y + 0.31, w: 0.5, h: 0.5, align: "center", valign: "middle", color: WHITE, fontSize: 18, bold: true });
    s.addText(h, { x: 1.75, y, w: 3.6, h: 1.12, valign: "middle", fontFace: HEAD, fontSize: 18, color: INK, bold: true });
    s.addText(d, { x: 5.4, y, w: 7.0, h: 1.12, valign: "middle", fontFace: BODY, fontSize: 15, color: SLATE });
    y += 1.25;
  });
}

// 20 — close
{
  const s = p.addSlide();
  s.background = { color: INK };
  s.addText("The question isn't whether your\ntools are safe individually.", { x: 0.8, y: 2.1, w: 11.7, h: 1.8, fontFace: HEAD, fontSize: 40, color: WHITE, bold: true, lineSpacingMultiple: 1.05 });
  s.addText("It's what they're capable of together — and whether you ask that question before an attacker does.", { x: 0.82, y: 4.1, w: 11.2, h: 1.4, fontFace: BODY, fontSize: 22, color: "818CF8", italic: true, lineSpacingMultiple: 1.1 });
}

// 21 — resources + disclaimer
{
  const s = p.addSlide();
  contentHead(s, "Try it yourself");
  s.addShape(p.ShapeType.roundRect, { x: 0.7, y: 1.7, w: 5.85, h: 2.3, fill: { color: INDIGOL }, line: { color: INDIGO, width: 1 }, rectRadius: 0.1 });
  s.addText([{ text: "Quanta\n", options: { bold: true, color: INDIGO, fontSize: 20, fontFace: HEAD } }, { text: "github.com/taoq-ai/quanta\n\n", options: { color: SLATE, fontSize: 15, fontFace: "Courier New" } }, { text: "The demo agent — defensible architecture, one composition finding.", options: { color: SLATE, fontSize: 15 } }], { x: 1.05, y: 1.95, w: 5.2, h: 1.8, valign: "top", fontFace: BODY, lineSpacingMultiple: 1.1 });
  s.addShape(p.ShapeType.roundRect, { x: 6.78, y: 1.7, w: 5.85, h: 2.3, fill: { color: "ECFDF5" }, line: { color: GREEN, width: 1 }, rectRadius: 0.1 });
  s.addText([{ text: "ZIRAN\n", options: { bold: true, color: GREEN, fontSize: 20, fontFace: HEAD } }, { text: "github.com/taoq-ai/ziran\n\n", options: { color: SLATE, fontSize: 15, fontFace: "Courier New" } }, { text: "The finder — composition analysis for AI agents.", options: { color: SLATE, fontSize: 15 } }], { x: 7.13, y: 1.95, w: 5.2, h: 1.8, valign: "top", fontFace: BODY, lineSpacingMultiple: 1.1 });
  s.addShape(p.ShapeType.roundRect, { x: 0.7, y: 4.3, w: 11.93, h: 1.5, fill: { color: REDL }, line: { color: RED, width: 1.2 }, rectRadius: 0.1 });
  s.addText([{ text: "⚠  Education only.  ", options: { bold: true, color: RED } }, { text: "Quanta is deliberately composable and has a known, intentional vulnerability by design. Do not deploy it for real or connect it to real data.", options: { color: "7F1D1D" } }], { x: 1.05, y: 4.3, w: 11.2, h: 1.5, valign: "middle", fontFace: BODY, fontSize: 16, lineSpacingMultiple: 1.1 });
  s.addText("Thank you — questions?", { x: 0.7, y: 6.1, w: 11.9, h: 0.8, align: "center", fontFace: HEAD, fontSize: 24, color: INK, bold: true });
}

p.writeFile({ fileName: path.join(__dirname, "quanta-talk.pptx") }).then((f) => console.log("wrote", f));
