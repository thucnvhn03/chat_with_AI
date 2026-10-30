#!/usr/bin/env node
// Gom kết quả kiểm thử (JUnit XML của pytest / Vitest / Playwright, báo cáo bộ đánh giá,
// kết quả thủ công) và gắn vào từng ca kiểm thử trong docs/testing/test_cases.
// Chỉ đọc tệp, không chạy kiểm thử. Không cần thư viện ngoài (Node >= 18).
//
//   node collect_results.mjs [--results test-results,backend/test-results] [--cases docs/testing/test_cases]
//        [--eval evaluation/reports] [--manual docs/testing/results/manual_results.csv]
//        [--out test-results/summary]
//
// Ra: <out>/summary.json (đầy đủ) và <out>/summary.md (bảng để dán vào báo cáo).
import fs from "node:fs";
import path from "node:path";

const args = parseArgs(process.argv.slice(2));
const casesDir = args.cases ?? "docs/testing/test_cases";
// Nhiều thư mục/tệp, phân tách bằng dấu phẩy (kết quả backend nằm trong backend/ do Docker gắn thư mục đó)
const resultsDir = args.results ?? "test-results,backend/test-results";
const outDir = args.out ?? "test-results/summary";

const STATUS = {
  PASS: "Đạt",
  FAIL: "Không đạt",
  SKIP: "Bỏ qua",
  MISSING: "Chưa có kết quả",
  MANUAL: "Thủ công — chưa ghi nhận",
  BLOCKED: "Bị chặn",
};

// ---------- 1. Đọc kết quả JUnit ----------
const tests = [];
const sources = [];
const xmlFiles = resultsDir.split(",").flatMap((d) => walk(d.trim())).filter((f) => f.endsWith(".xml"));
for (const file of xmlFiles) {
  const xml = fs.readFileSync(file, "utf8");
  const before = tests.length;
  for (const m of xml.matchAll(/<testcase\b([^>]*?)(\/>|>([\s\S]*?)<\/testcase>)/g)) {
    const attrs = parseAttrs(m[1]);
    const body = m[3] ?? "";
    const failure = body.match(/<(failure|error)\b([^>]*)>?/);
    const status = failure ? "fail" : /<skipped\b/.test(body) ? "skip" : "pass";
    const message = failure ? decode(parseAttrs(failure[2]).message ?? firstLine(body)) : "";
    tests.push({
      source: path.relative(process.cwd(), file),
      fileKey: fileKeyOf(attrs),
      name: decode(attrs.name ?? ""),
      status,
      time: Number(attrs.time ?? 0),
      message: message.slice(0, 300),
      used: false,
    });
  }
  const mine = tests.slice(before);
  sources.push({
    file: path.relative(process.cwd(), file),
    layer: layerOf(file, mine),
    total: mine.length,
    pass: mine.filter((t) => t.status === "pass").length,
    fail: mine.filter((t) => t.status === "fail").length,
    skip: mine.filter((t) => t.status === "skip").length,
    seconds: round(mine.reduce((s, t) => s + t.time, 0)),
    modified: fs.statSync(file).mtime.toISOString(),
  });
}

// ---------- 2. Đọc ca kiểm thử ----------
const cases = [];
for (const file of walk(casesDir).filter((f) => /[A-Z0-9]+(-[A-Z]+)?-\d+\.md$/.test(f))) {
  const text = fs.readFileSync(file, "utf8");
  const head = text.match(/^# ([A-Z0-9-]+-\d+) — (.+)$/m);
  if (!head) continue;
  const auto = cell(text, "Tự động hóa");
  const detail = cell(text, "Ca chi tiết");
  cases.push({
    id: head[1],
    title: head[2].trim(),
    group: path.basename(path.dirname(file)),
    priority: (cell(text, "Ưu tiên[^|]*") ?? "").split("/")[0].trim(),
    automation: auto ?? "",
    refs: auto ? parseRefs(auto) : [],
    manual: !auto || /thủ công/i.test(auto),
    deps: expandIds(`${auto ?? ""} ${detail ?? ""}`),
  });
}
const caseById = new Map(cases.map((c) => [c.id, c]));

// ---------- 3. Kết quả thủ công ----------
const manual = new Map();
if (args.manual && fs.existsSync(args.manual)) {
  const [header, ...rows] = fs.readFileSync(args.manual, "utf8").trim().split(/\r?\n/);
  const cols = header.split(",").map((s) => s.trim());
  for (const row of rows) {
    const vals = splitCsv(row);
    const rec = Object.fromEntries(cols.map((c, i) => [c, (vals[i] ?? "").trim()]));
    if (rec.id) manual.set(rec.id, rec);
  }
}

// ---------- 4. Gắn kết quả vào ca ----------
for (const c of cases) evaluate(c);
function evaluate(c, seen = new Set()) {
  if (c.status) return c;
  if (seen.has(c.id)) return c;
  seen.add(c.id);
  c.evidence = [];
  c.missing = [];
  let failed = false;
  const skipped = [];
  for (const ref of c.refs) {
    const hits = tests.filter((t) => matches(ref, t));
    if (!hits.length) { c.missing.push(ref.label); continue; }
    hits.forEach((t) => (t.used = true));
    const f = hits.filter((t) => t.status === "fail");
    if (f.length) { failed = true; c.evidence.push(...f.map((t) => `✗ ${t.fileKey} › ${t.name}: ${t.message}`)); }
    if (hits.every((t) => t.status === "skip")) skipped.push(ref.label);
  }
  if (skipped.length) c.evidence.push(`bỏ qua: ${skipped.join(", ")}`);
  const depStatuses = c.deps.filter((id) => id !== c.id && caseById.has(id))
    .map((id) => [id, evaluate(caseById.get(id), seen).status]);
  const m = manual.get(c.id);

  if (m?.status) {
    c.status = m.status;
    c.evidence.push(`Thủ công: ${[m.date, m.tester, m.note].filter(Boolean).join(" · ")}`);
  } else if (failed || depStatuses.some(([, s]) => s === STATUS.FAIL)) {
    c.status = STATUS.FAIL;
    depStatuses.filter(([, s]) => s === STATUS.FAIL).forEach(([id]) => c.evidence.push(`✗ phụ thuộc ${id}`));
  } else if (c.refs.length && c.missing.length) {
    c.status = STATUS.MISSING;
  } else if (skipped.length) {
    // Một phần ca không chạy thì chưa thể kết luận Đạt
    c.status = STATUS.SKIP;
  } else if (c.refs.length) {
    c.status = STATUS.PASS;
  } else if (depStatuses.length) {
    const s = depStatuses.map(([, s]) => s);
    c.status = s.every((x) => x === STATUS.PASS) ? STATUS.PASS
      : s.some((x) => x === STATUS.MISSING || x === STATUS.SKIP) ? STATUS.MISSING : STATUS.MANUAL;
    c.evidence.push(`Theo ${depStatuses.map(([id, s]) => `${id}: ${s}`).join(", ")}`);
  } else {
    c.status = STATUS.MANUAL;
  }
  if (c.status === STATUS.PASS && c.manual && c.refs.length && !m) c.note = "Phần tự động đạt; phần thủ công chưa ghi nhận";
  return c;
}

// ---------- 5. Bộ đánh giá ----------
let evalReport = null;
if (args.eval) {
  const file = fs.statSync(args.eval).isDirectory()
    ? walk(args.eval).filter((f) => f.endsWith(".json")).sort().at(-1)
    : args.eval;
  if (file) {
    const r = JSON.parse(fs.readFileSync(file, "utf8"));
    evalReport = { file: path.relative(process.cwd(), file), generated_at: r.generated_at,
      config_note: r.config_note, git_revision: r.git_revision, cost_usd: r.cost_usd,
      metrics: r.metrics, by_language: r.by_language };
  }
}

// ---------- 6. Xuất ----------
const unmapped = tests.filter((t) => !t.used);
const groups = {};
for (const c of cases) {
  groups[c.group] ??= { total: 0 };
  groups[c.group].total++;
  groups[c.group][c.status] = (groups[c.group][c.status] ?? 0) + 1;
}
const summary = {
  generated_at: new Date().toISOString(),
  inputs: { results: resultsDir, cases: casesDir, eval: args.eval ?? null, manual: args.manual ?? null },
  sources, groups,
  cases: cases.map(({ refs, deps, ...c }) => c),
  failures: tests.filter((t) => t.status === "fail").map(({ used, ...t }) => t),
  unmapped_tests: unmapped.map((t) => `${t.fileKey} › ${t.name}`),
  eval: evalReport,
};
fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, "summary.json"), JSON.stringify(summary, null, 2));
fs.writeFileSync(path.join(outDir, "summary.md"), toMarkdown(summary));
console.log(`Nguồn kết quả: ${sources.length} tệp, ${tests.length} kiểm thử (${summary.failures.length} lỗi)`);
console.log(`Ca kiểm thử: ${cases.length}`);
for (const [s, n] of Object.entries(countBy(cases, "status"))) console.log(`  ${s}: ${n}`);
console.log(`Kiểm thử chưa gắn với ca nào: ${unmapped.length}`);
console.log(`Đã ghi ${path.join(outDir, "summary.md")} và summary.json`);

// ---------- Hàm phụ ----------
function parseRefs(cellText) {
  const refs = [];
  for (const seg of cellText.split(";")) {
    let file = null;
    let fileRefs = 0;
    // Token trong dấu `...` và tiêu đề trong "..." theo đúng thứ tự xuất hiện
    for (const m of seg.matchAll(/`([^`]+)`|"([^"]+)"/g)) {
      if (m[1]) {
        const tok = m[1].trim();
        if (tok.includes("*") || /\s/.test(tok)) continue;
        const [f, fn] = tok.split("::");
        if (/\.(py|tsx?|ya?ml)$/.test(f)) {
          if (file && fileRefs === 0) refs.push({ file, label: file });
          file = path.basename(f);
          fileRefs = 0;
          if (fn) { refs.push({ file, name: fn, label: `${file}::${fn}` }); fileRefs++; }
        } else if (/^test_\w+$/.test(tok)) {
          refs.push({ file, name: tok, label: file ? `${file}::${tok}` : tok });
          fileRefs++;
        }
      } else if (m[2] && file && /\.tsx?$/.test(file)) {
        refs.push({ file, title: m[2], label: `${file}: "${m[2]}"` });
        fileRefs++;
      }
    }
    if (file && fileRefs === 0) refs.push({ file, label: file });
  }
  // .yml (promtool) không có JUnit — coi là bằng chứng ngoài, không đòi kết quả
  return refs.filter((r) => !/\.ya?ml$/.test(r.file ?? ""));
}

function matches(ref, t) {
  if (ref.file && t.fileKey !== ref.file) return false;
  if (ref.name) return t.name.replace(/\[.*\]$/, "") === ref.name;
  if (ref.title) return t.name.toLowerCase().includes(ref.title.toLowerCase());
  return true;
}

function fileKeyOf(a) {
  if (a.file) return path.basename(a.file);
  const cls = decode(a.classname ?? "");
  if (/\.(tsx?|jsx?|mjs)$/.test(cls) || cls.includes("/")) return path.basename(cls);
  // pytest: tests.integration.test_auth[.TestClass]
  const parts = cls.split(".");
  const mod = [...parts].reverse().find((p) => p.startsWith("test_"));
  return mod ? `${mod}.py` : cls;
}

function layerOf(file, mine) {
  const name = path.basename(file).toLowerCase();
  for (const key of ["unit", "integration", "security", "frontend", "vitest", "e2e", "playwright", "evaluation", "eval"]) {
    if (name.includes(key)) return key;
  }
  const k = mine[0]?.fileKey ?? "";
  return k.endsWith(".spec.ts") ? "e2e" : /\.test\.tsx?$/.test(k) ? "frontend" : k.endsWith(".py") ? "backend" : "khác";
}

function cell(text, label) {
  const m = text.match(new RegExp(`^\\|\\s*${label}\\s*\\|(.*)\\|\\s*$`, "m"));
  return m ? m[1].trim() : null;
}

function expandIds(text) {
  const ids = new Set();
  for (const m of text.matchAll(/\b((?:INT-API|UT|E2E|UAT|PERF|SEC|ACC|UI|API|QE|OPS))-(\d{3})(?:\.\.(?:\1-)?(\d{3}))?/g)) {
    const [, p, a, b] = m;
    for (let i = Number(a); i <= Number(b ?? a); i++) ids.add(`${p}-${String(i).padStart(3, "0")}`);
  }
  return [...ids];
}

function toMarkdown(s) {
  const L = [];
  L.push(`# Tổng hợp kết quả kiểm thử`, ``, `Sinh lúc ${s.generated_at} bởi \`collect_results.mjs\`.`, ``);
  L.push(`## Nguồn kết quả`, ``);
  if (!s.sources.length) L.push(`_Không tìm thấy tệp JUnit XML trong \`${s.inputs.results}\`._`, ``);
  else {
    L.push(`| Tệp | Tầng | Tổng | Đạt | Lỗi | Bỏ qua | Thời gian (s) | Sửa lần cuối |`, `|---|---|---|---|---|---|---|---|`);
    for (const r of s.sources) L.push(`| \`${r.file}\` | ${r.layer} | ${r.total} | ${r.pass} | ${r.fail} | ${r.skip} | ${r.seconds} | ${r.modified.slice(0, 16)} |`);
    L.push(``);
  }
  const statuses = Object.values(STATUS);
  L.push(`## Trạng thái ca theo nhóm`, ``, `| Nhóm | Tổng | ${statuses.join(" | ")} |`, `|---|---|${statuses.map(() => "---").join("|")}|`);
  for (const [g, v] of Object.entries(s.groups)) L.push(`| ${g} | ${v.total} | ${statuses.map((x) => v[x] ?? 0).join(" | ")} |`);
  const tot = countBy(s.cases, "status");
  L.push(`| **Tổng** | **${s.cases.length}** | ${statuses.map((x) => `**${tot[x] ?? 0}**`).join(" | ")} |`, ``);
  if (s.failures.length) {
    L.push(`## Kiểm thử lỗi`, ``, `| Tệp | Kiểm thử | Thông điệp |`, `|---|---|---|`);
    for (const f of s.failures) L.push(`| ${f.fileKey} | ${esc(f.name)} | ${esc(f.message)} |`);
    L.push(``);
  }
  L.push(`## Từng ca`, ``, `| Mã | Tên | Ưu tiên | Trạng thái | Ghi chú |`, `|---|---|---|---|---|`);
  for (const c of s.cases) {
    const note = [...(c.evidence ?? []), c.missing?.length ? `thiếu kết quả: ${c.missing.join(", ")}` : "", c.note ?? ""].filter(Boolean).join("; ");
    L.push(`| ${c.id} | ${esc(c.title)} | ${c.priority} | ${c.status} | ${esc(note)} |`);
  }
  L.push(``);
  if (s.eval) {
    const m = s.eval.metrics;
    L.push(`## Bộ đánh giá`, ``, `- Tệp: \`${s.eval.file}\` (${s.eval.generated_at})`, `- Cấu hình: ${s.eval.config_note ?? "không ghi"}`, `- Chi phí: ${s.eval.cost_usd ?? "không ghi"}`, ``);
    L.push(`| Chỉ số | Giá trị |`, `|---|---|`);
    for (const k of ["correct_with_source", "hallucination_rate", "source_coverage", "follow_up_correct", "correct_page", "answers_with_content_having_source"])
      L.push(`| ${k} | ${pct(m[k])} |`);
    L.push(`| latency p50/p90/p95 (ms) | ${["p50", "p90", "p95"].map((p) => Math.round(m.latency_ms?.[p] ?? NaN)).join(" / ")} |`, ``);
  }
  L.push(`## Kiểm thử chưa gắn với ca nào (${s.unmapped_tests.length})`, ``);
  L.push(s.unmapped_tests.length ? s.unmapped_tests.slice(0, 200).map((t) => `- ${esc(t)}`).join("\n") : "_Không có._", ``);
  return L.join("\n");
}

function parseArgs(argv) {
  const o = {};
  for (let i = 0; i < argv.length; i++) if (argv[i].startsWith("--")) o[argv[i].slice(2)] = argv[i + 1]?.startsWith("--") ? true : argv[++i];
  return o;
}
function walk(dir) {
  if (!fs.existsSync(dir)) return [];
  if (fs.statSync(dir).isFile()) return [dir];
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((d) =>
    d.isDirectory() ? (d.name === "node_modules" ? [] : walk(path.join(dir, d.name))) : [path.join(dir, d.name)]);
}
function parseAttrs(s) { return Object.fromEntries([...s.matchAll(/([\w:-]+)="([^"]*)"/g)].map((m) => [m[1], m[2]])); }
function decode(s) { return s.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(n)).replace(/&#x([0-9a-f]+);/gi, (_, n) => String.fromCodePoint(parseInt(n, 16))).replace(/&amp;/g, "&"); }
function firstLine(s) { return s.replace(/<[^>]+>/g, "").trim().split("\n")[0] ?? ""; }
function splitCsv(row) { return [...row.matchAll(/("([^"]*(?:""[^"]*)*)"|[^,]*)(,|$)/g)].map((m) => (m[2] ?? m[1]).replace(/""/g, '"')).slice(0, -1); }
function countBy(arr, k) { return arr.reduce((o, x) => ((o[x[k]] = (o[x[k]] ?? 0) + 1), o), {}); }
function esc(s) { return String(s).replace(/\|/g, "\\|").replace(/\n/g, " "); }
function pct(v) { return v == null ? "—" : `${(v * 100).toFixed(1)}%`; }
function round(v) { return Math.round(v * 10) / 10; }
