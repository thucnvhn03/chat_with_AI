#!/usr/bin/env node
// Lập hồ sơ kết quả một lần chạy kiểm thử từ test-results/<run>/ (do run_layers.sh tạo):
//   docs/testing/results/<run>/README.md       tổng quan, checklist chung, ảnh từng tầng, ca còn chờ
//   docs/testing/results/<run>/<nhóm>.md       từng ca: checklist, kiểm thử đã chạy, ảnh kết quả
//   docs/testing/results/<run>/screenshots/    ca/<Mã ca>.png, ket-qua/<tầng>.png, e2e/, man-hinh/
//
//   node .claude/skills/test-run/scripts/build_run_docs.mjs [--run run-YYYY-MM-DD] [--no-images]
// Chạy từ gốc repo. Gắn kết quả vào ca bằng collect_results.mjs của skill test-report.
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { renderCases, renderLayers } from "./render.mjs";

const args = parseArgs(process.argv.slice(2));
const RUN = args.run ?? latestRun();
const RAW = path.join("test-results", RUN);
const DOCS = path.join("docs/testing/results", RUN);
const CASES_DIR = "docs/testing/test_cases";
const MANUAL_CSV = "docs/testing/results/manual_results.csv";
const COLLECTOR = ".claude/skills/test-report/scripts/collect_results.mjs";

const LAYERS = [
  { key: "backend", file: "backend-pytest", label: "Backend — pytest (unit, tích hợp, bảo mật)", short: "Backend (unit, tích hợp, bảo mật)", tool: "pytest, PostgreSQL + pgvector, S3" },
  { key: "frontend", file: "frontend-vitest", label: "Frontend — Vitest", short: "Frontend", tool: "Vitest + axe" },
  { key: "e2e", file: "e2e-playwright", label: "E2E — Playwright (Chromium)", short: "Đầu-cuối (giao diện thật)", tool: "Playwright + axe" },
  { key: "eval", file: "evaluation-pytest", label: "Bộ đánh giá — pytest (công thức chỉ số)", short: "Bộ đánh giá (công thức chỉ số)", tool: "pytest" },
];
const STATUS = ["Đạt", "Không đạt", "Bỏ qua", "Chưa có kết quả", "Thủ công — chưa ghi nhận", "Bị chặn"];
const ICON = { "Đạt": "✅", "Không đạt": "❌", "Bỏ qua": "⏭️", "Chưa có kết quả": "⚪", "Thủ công — chưa ghi nhận": "📝", "Bị chặn": "⛔" };

// ---------- 1. Nguồn kết quả ----------
if (!fs.existsSync(RAW)) die(`Không có ${RAW}. Chạy run_layers.sh trước.`);
const meta = readJson(path.join(RAW, "run-meta.json")) ?? {};
const present = LAYERS.filter((l) => fs.existsSync(path.join(RAW, `${l.file}.xml`)));
if (!present.length) die(`Không có tệp JUnit nào trong ${RAW}.`);
const xmls = present.map((l) => path.join(RAW, `${l.file}.xml`));
const promtoolLog = path.join(RAW, "ops-promtool.log");
const promtool = fs.existsSync(promtoolLog) ? (/SUCCESS/.test(read(promtoolLog)) ? "SUCCESS" : "FAILED") : null;
const commit = meta.commit ?? git("rev-parse", "--short", "HEAD");
const runDate = RUN.replace(/^run-/, "");
const runLabel = `Lần chạy ${runDate}`;

execFileSync("node", [COLLECTOR, "--results", xmls.join(","), "--eval", "evaluation/reports",
  "--manual", MANUAL_CSV, "--out", path.join(RAW, "summary")], { stdio: "inherit" });
const summary = readJson(path.join(RAW, "summary", "summary.json"));
const statusById = new Map(summary.cases.map((c) => [c.id, c]));

// Làm mới phần sinh tự động, giữ NOTES.md người chạy viết tay
fs.mkdirSync(DOCS, { recursive: true });
for (const f of fs.readdirSync(DOCS)) {
  if (/^\d\d_.*\.md$|^README\.md$|^tong-hop-summary\.md$|\.(xml|log)$/.test(f)) fs.rmSync(path.join(DOCS, f));
}
for (const d of ["ca", "ket-qua", "e2e", "man-hinh"]) fs.rmSync(path.join(DOCS, "screenshots", d), { recursive: true, force: true });
for (const f of fs.readdirSync(RAW)) if (/\.(xml|log)$/.test(f) && !f.startsWith("e2e-stack")) fs.copyFileSync(path.join(RAW, f), path.join(DOCS, f));
fs.copyFileSync(path.join(RAW, "summary", "summary.md"), path.join(DOCS, "tong-hop-summary.md"));

// ---------- 2. Kiểm thử trong JUnit ----------
const tests = [];
for (const l of present) {
  const xml = read(path.join(RAW, `${l.file}.xml`));
  for (const m of xml.matchAll(/<testcase\b([^>]*?)(\/>|>([\s\S]*?)<\/testcase>)/g)) {
    const a = parseAttrs(m[1]);
    const body = m[3] ?? "";
    const f = body.match(/<(failure|error)\b([^>]*)>?/);
    const skipped = /<skipped\b/.test(body);
    tests.push({
      layer: l.key === "eval" ? "Bộ đánh giá" : l.key === "e2e" ? "E2E" : l.key[0].toUpperCase() + l.key.slice(1),
      fileKey: fileKeyOf(a), name: decode(a.name ?? ""), time: Number(a.time ?? 0),
      status: f ? "fail" : skipped ? "skip" : "pass",
      message: f ? decode(parseAttrs(f[2]).message ?? "").slice(0, 300)
        : skipped ? decode((body.match(/<skipped[^>]*message="([^"]*)"/) ?? [])[1] ?? "") : "",
    });
  }
}

// ---------- 3. Ảnh giao diện ----------
// Ảnh trạng thái cuối của từng ca E2E (Playwright JSON có đường dẫn ảnh đính kèm)
const shotsByTitle = new Map();
const e2eJson = path.join(RAW, "e2e-playwright.json");
if (fs.existsSync(e2eJson)) {
  const dir = path.join(DOCS, "screenshots", "e2e");
  fs.mkdirSync(dir, { recursive: true });
  let n = 0;
  let prevSizes = [];
  const visit = (suite, file) => {
    for (const s of suite.suites ?? []) visit(s, s.file ?? file);
    for (const spec of suite.specs ?? []) {
      n++;
      const specFile = path.basename(spec.file ?? file);
      const imgs = [];
      const sizes = [];
      for (const t of spec.tests) for (const r of t.results) for (const at of r.attachments ?? []) {
        if (at.name !== "screenshot" || !at.path || !fs.existsSync(at.path)) continue;
        // Trang mở bằng browser.newPage() không đóng bị chụp lại ở các ca sau: bỏ ảnh trùng (±50 byte) với ca liền trước.
        // Dung sai lớn hơn sẽ loại nhầm ảnh thật của ca (đã gặp: hai màn hình khác nhau chỉ lệch ~185 byte).
        const size = fs.statSync(at.path).size;
        sizes.push(size);
        if (prevSizes.some((p) => Math.abs(p - size) <= 50)) continue;
        const out = `${String(n).padStart(2, "0")}_${specFile.replace(/\.ts$/, "")}_${slug(spec.title)}_${imgs.length + 1}.png`;
        fs.copyFileSync(at.path, path.join(dir, out));
        imgs.push(`screenshots/e2e/${out}`);
      }
      prevSizes = sizes;
      shotsByTitle.set(`${specFile}::${spec.title}`, imgs);
    }
  };
  for (const s of readJson(e2eJson).suites) visit(s, s.file);
}
// Ảnh màn hình S-01..S-07 do screenshots.spec.ts chụp — chỉ lấy khi tầng E2E chạy trong lần này
const SCREENS = [["s01-default", "S-01 Đăng nhập"], ["s01-wrong", "S-01 Sai thông tin"], ["s02-empty", "S-02 Trống"],
  ["s02-default", "S-02 Có tài liệu"], ["s04-default", "S-04 Xác nhận xóa"], ["s05-default", "S-05 Quản trị quyền"],
  ["s06-default", "S-06 Nhật ký kiểm toán"], ["s07-default", "S-07 Báo cáo sử dụng"]];
const screens = [];
if (fs.existsSync(e2eJson)) {
  fs.mkdirSync(path.join(DOCS, "screenshots", "man-hinh"), { recursive: true });
  for (const [n, cap] of SCREENS) {
    const src = path.join("docs/implement/evidence/screenshots", `${n}.png`);
    if (!fs.existsSync(src)) continue;
    fs.copyFileSync(src, path.join(DOCS, "screenshots", "man-hinh", `${n}.png`));
    screens.push({ p: `screenshots/man-hinh/${n}.png`, cap });
  }
}
const SCREEN_SHOTS = { "UI-001": screens, "UI-002": screens.filter((s) => /s01-default|s02-default/.test(s.p)) };
// Bằng chứng không có JUnit
const EXTRA = {};
if (promtool) EXTRA["OPS-002"] = `**Bằng chứng ngoài JUnit:** \`promtool test rules alerts_test.yml\` → \`${promtool}\` — [ops-promtool.log](ops-promtool.log)`;

// ---------- 4. Từng ca ----------
const groups = fs.readdirSync(CASES_DIR).filter((d) => /^\d\d_/.test(d)).sort();
const caseData = [];
const groupRows = [];
let checked = 0, unchecked = 0;
for (const g of groups) {
  const gTitle = (read(path.join(CASES_DIR, g, "README.md")).match(/^# (.+)$/m) ?? [, g])[1];
  const files = fs.readdirSync(path.join(CASES_DIR, g)).filter((f) => /-\d{3}\.md$/.test(f)).sort();
  const rows = [];
  const body = [];
  const count = {};
  for (const f of files) {
    const text = read(path.join(CASES_DIR, g, f));
    const id = f.replace(/\.md$/, "");
    const s = statusById.get(id);
    const status = s?.status ?? "Chưa có kết quả";
    count[status] = (count[status] ?? 0) + 1;
    const title = (text.match(/^# [A-Z0-9-]+ — (.+)$/m) ?? [, ""])[1];
    const auto = cell(text, "Tự động hóa") ?? "";
    const refs = parseRefs(auto);
    const matched = refs.flatMap((r) => tests.filter((t) => matches(r, t)));
    const pass = matched.filter((t) => t.status === "pass").length;
    const partial = /thủ công/.test(s?.note ?? "");
    const manualCase = /Thủ công/.test(status);

    const checklist = buildChecklist(text, g, status, partial, manualCase);
    checked += checklist.filter((c) => c.mark).length;
    unchecked += checklist.filter((c) => !c.mark).length;

    const imgs = [];
    for (const r of refs.filter((r) => /\.spec\.ts$/.test(r.file ?? ""))) {
      for (const [k, v] of shotsByTitle) {
        const [spec, t] = k.split("::");
        if (spec === r.file && (!r.title || t.toLowerCase().includes(r.title.toLowerCase()))) imgs.push(...v.map((p) => ({ p, cap: t })));
      }
    }
    imgs.push(...(SCREEN_SHOTS[id] ?? []));

    const statusText = `${ICON[status] ?? "⚪"} ${status}`;
    rows.push(`| [${id}](#${id.toLowerCase()}) | ${esc(title)} | ${s?.priority || "—"} | ${statusText}${partial ? " (tự động) — thủ công chưa ghi nhận" : ""} | ${matched.length ? `${pass}/${matched.length}` : "—"} | ${imgs.length + 1} |`);
    const manualEv = (s?.evidence ?? []).filter((e) => e.startsWith("Thủ công:"));
    caseData.push({
      id, group: g, title, status, partial, priority: s?.priority ?? "",
      checklist: checklist.map((c) => ({ mark: c.mark, text: (c.text + c.note).replace(/[_`*]/g, "") })),
      tests: matched.map(({ layer, fileKey, name, status, time, message }) => ({ layer, file: fileKey, name, status, time, message })),
      evidence: matched.length ? manualEv : (s?.evidence ?? []),
      missing: s?.missing ?? [],
      extra: EXTRA[id] ? EXTRA[id].replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").replace(/[*`]/g, "") : "",
    });

    body.push(`## ${id}`, "", `**${esc(title)}** — ${ICON[status] ?? "⚪"} **${status}**${partial ? " phần tự động — _phần thủ công chưa ghi nhận_" : ""}`, "");
    body.push(`| Mục | Nội dung |`, `|---|---|`);
    for (const k of ["Mục tiêu", "Truy vết", "Story / AC", "Ưu tiên", "Ưu tiên / Loại"]) { const v = cell(text, k); if (v) body.push(`| ${k} | ${v} |`); }
    const detail = cell(text, "Ca chi tiết");
    body.push(`| Tự động hóa | ${auto || (detail ? `Theo ${detail}` : "Thủ công")} |`);
    body.push(`| Đặc tả | [${f}](../../test_cases/${g}/${f}) |`, "");
    if (s?.note) body.push(`> ${s.note}`, "");
    if (s?.missing?.length) body.push(`> ⚠️ Không tìm thấy kết quả cho: ${s.missing.join(", ")} — tầng chưa chạy hoặc tên kiểm thử trong đặc tả đã cũ`, "");

    body.push(`**Checklist kết quả mong đợi**`, "");
    body.push(...(checklist.length ? checklist.map((c) => `- [${c.mark ? "x" : " "}] ${c.text}${c.note}`) : ["- _(đặc tả không có danh sách kết quả mong đợi)_"]), "");
    if (matched.length) {
      body.push(`**Kiểm thử tự động đã chạy** (${pass}/${matched.length} đạt)`, "", `| | Tầng | Tệp | Kiểm thử | Thời gian |`, `|---|---|---|---|---|`);
      for (const t of matched) body.push(`| ${t.status === "pass" ? "✅" : t.status === "skip" ? "⏭️" : "❌"} | ${t.layer} | \`${t.fileKey}\` | ${esc(t.name)}${t.message ? `<br>_${esc(t.message)}_` : ""} | ${t.time.toFixed(2)} s |`);
      body.push("");
      if (manualEv.length) body.push(`**Kết quả thủ công đã ghi nhận:** ${manualEv.map(esc).join("; ")}`, "");
    } else if (s?.evidence?.length) {
      body.push(`**Căn cứ:** ${s.evidence.map(esc).join("; ")}`, "");
    }
    if (EXTRA[id]) body.push(EXTRA[id], "");
    if (status === "Không đạt") body.push(`**Lỗi:** ${(s?.evidence ?? []).map(esc).join("; ")}`, "");
    body.push(`**Ảnh kết quả**`, "", `![Kết quả ${id}](screenshots/ca/${id}.png)`, `_Kết quả ${id} — ${runLabel.toLowerCase()}_`, "");
    for (const { p, cap } of imgs) body.push(`![${esc(cap)}](${encodeURI(p)})`, `_${esc(cap)}_`, "");
    if (manualCase) body.push(`**Cách ghi nhận:** thực hiện theo đặc tả rồi thêm dòng \`${id},<Đạt|Không đạt|Bị chặn>,<ngày>,<người>,<ghi chú>\` vào \`${MANUAL_CSV}\`.`, "");
    body.push("---", "");
  }
  fs.writeFileSync(path.join(DOCS, `${g}.md`), [
    `# ${gTitle} — kết quả chi tiết`, "",
    `${runLabel} (commit \`${commit}\`): [README](README.md) · Đặc tả: [${g}](../../test_cases/${g}/README.md)`, "",
    `| Mã | Tên | Ưu tiên | Kết quả | Kiểm thử tự động đạt | Ảnh |`, `|---|---|---|---|---|---|`, ...rows, "", ...body].join("\n"));
  groupRows.push({ g, gTitle, total: files.length, count });
}

// ---------- 5. Ảnh ----------
if (!args["no-images"]) {
  await renderCases(caseData, path.join(DOCS, "screenshots", "ca"), { runLabel, commit });
  await renderLayers(present.map((l) => ({ label: l.label, file: path.join(RAW, `${l.file}.xml`), slug: l.file })),
    path.join(DOCS, "screenshots", "ket-qua"), { runLabel });
}

// ---------- 6. README ----------
fs.writeFileSync(path.join(DOCS, "README.md"), readme());
const tot = countBy(caseData, "status");
console.log(`\nHồ sơ: ${DOCS}`);
console.log(`Ca: ${caseData.length} — ${Object.entries(tot).map(([k, v]) => `${k} ${v}`).join(", ")}`);
console.log(`Checklist: ${checked} đánh dấu, ${unchecked} để trống. Ảnh E2E: ${[...shotsByTitle.values()].flat().length}`);
if (summary.failures.length) console.log(`KIỂM THỬ LỖI: ${summary.failures.length} — xem mục "Kiểm thử lỗi" trong README`);

function readme() {
  const src = Object.fromEntries(summary.sources.map((s) => [path.basename(s.file, ".xml"), s]));
  const all = summary.sources.reduce((a, s) => ({ total: a.total + s.total, pass: a.pass + s.pass, fail: a.fail + s.fail, skip: a.skip + s.skip }), { total: 0, pass: 0, fail: 0, skip: 0 });
  const tot = countBy(caseData, "status");
  const partials = caseData.filter((c) => c.partial).map((c) => c.id);
  const pending = caseData.filter((c) => /Thủ công/.test(c.status));
  const missing = caseData.filter((c) => c.status === "Chưa có kết quả");
  const skipped = tests.filter((t) => t.status === "skip");
  const ev = summary.eval;
  const dk = meta.docker;
  const notes = fs.existsSync(path.join(DOCS, "NOTES.md")) ? read(path.join(DOCS, "NOTES.md")).trim() : "";
  const notRun = LAYERS.filter((l) => !present.includes(l));
  const L = [];
  L.push(`# Kết quả kiểm thử — ${runDate}`, "");
  L.push(`| Mục | Nội dung |`, `|---|---|`);
  const usesDocker = present.some((l) => l.key !== "frontend");
  L.push(`| Phiên bản mã | ${meta.commit ? `\`${commit}\` trên \`${meta.branch}\`` : `_không rõ (thiếu run-meta.json); HEAD hiện tại là \`${commit}\`_`}${meta.dirty ? " **(có thay đổi chưa commit trong mã)**" : ""}${meta.image_created ? ` · ảnh Docker tạo ${meta.image_created.slice(0, 10)}` : ""} |`);
  L.push(`| Môi trường | ${dk ? `Docker ${dk.server} (${dk.cpus} CPU, ${dk.mem_gb} GB). ` : usesDocker ? "Docker (cấu hình không ghi nhận). " : "Chỉ Node, không Docker. "}${usesDocker ? `Compose \`deploy/docker-compose.yml\`${present.some((l) => l.key === "e2e") ? " + `deploy/docker-compose.e2e.yml`" : ""}` : ""} |`);
  L.push(`| Cấu hình AI | Kiểm thử tích hợp và E2E dùng adapter AI giả lập (\`fake\`) và embedding \`hash\`: kiểm chứng chức năng và luồng, **không** phải số liệu chất lượng câu trả lời |`);
  L.push(`| Đặc tả ca | [docs/testing/test_cases/](../../test_cases/README.md) — ${caseData.length} ca |`, "");

  L.push(`## 1. Tóm tắt`, "");
  L.push(`**${all.total} kiểm thử tự động: ${all.pass} đạt, ${all.fail} lỗi, ${all.skip} bỏ qua.**`);
  L.push(`Gắn vào ${caseData.length} ca: ${STATUS.filter((s) => tot[s]).map((s) => `**${tot[s]} ${s}**`).join(", ")}.`);
  if (partials.length) L.push(`Trong số ca Đạt có ${partials.length} ca mới đạt phần tự động, phần thủ công còn chờ: ${partials.join(", ")}.`);
  if (notRun.length) L.push(`Tầng **không chạy** trong lần này: ${notRun.map((l) => l.short).join(", ")} — các ca phụ thuộc hiện "Chưa có kết quả".`);
  L.push("");
  L.push(`| Tầng | Công cụ | Tổng | Đạt | Lỗi | Bỏ qua | Thời gian | Tệp |`, `|---|---|---|---|---|---|---|---|`);
  for (const l of LAYERS) {
    const s = src[l.file];
    if (!s) { L.push(`| ${l.short} | ${l.tool} | — | — | — | — | — | _không chạy_ |`); continue; }
    const secs = meta.layers?.[l.key]?.seconds ?? s.seconds;
    const log = fs.existsSync(path.join(DOCS, `${l.file}.log`)) ? `, [log](${l.file}.log)` : "";
    L.push(`| ${l.short} | ${l.tool} | ${s.total} | **${s.pass}** | ${s.fail} | ${s.skip} | ${dur(secs)} | [xml](${l.file}.xml)${log} |`);
  }
  if (promtool) L.push(`| Luật cảnh báo | promtool | 1 tệp | **${promtool}** | — | — | — | [log](ops-promtool.log) |`);
  L.push(`| **Tổng** | | **${all.total}** | **${all.pass}** | **${all.fail}** | **${all.skip}** | | |`, "");
  if (skipped.length) L.push(`Bỏ qua: ${skipped.map((t) => `\`${t.fileKey}::${t.name}\`${t.message ? ` (${esc(t.message)})` : ""}`).join("; ")}.`, "");

  if (summary.failures.length) {
    L.push(`### Kiểm thử lỗi`, "", `| Tệp | Kiểm thử | Thông điệp |`, `|---|---|---|`);
    for (const f of summary.failures) L.push(`| \`${f.fileKey}\` | ${esc(f.name)} | ${esc(f.message)} |`);
    L.push("");
  }

  L.push(`## 2. Kết quả theo nhóm ca`, "", `Bấm vào nhóm để xem từng ca: checklist kết quả mong đợi, kiểm thử tự động đã chạy, ảnh kết quả.`, "");
  const cols = STATUS.filter((s) => caseData.some((c) => c.status === s));
  L.push(`| Nhóm | Tổng | ${cols.map((s) => `${ICON[s]} ${s}`).join(" | ")} | Chi tiết |`, `|---|---|${cols.map(() => "---").join("|")}|---|`);
  for (const r of groupRows) L.push(`| ${esc(r.gTitle.replace(/^\d+ — /, ""))} | ${r.total} | ${cols.map((s) => r.count[s] ?? 0).join(" | ")} | [${r.g}.md](${r.g}.md) |`);
  L.push(`| **Tổng** | **${caseData.length}** | ${cols.map((s) => `**${tot[s] ?? 0}**`).join(" | ")} | [tong-hop-summary.md](tong-hop-summary.md) |`, "");
  L.push(`Checklist trong các tệp chi tiết: **${checked} mục đã đánh dấu**, **${unchecked} mục để trống**.`, "");
  L.push(`| Ký hiệu | Nghĩa |`, `|---|---|`);
  L.push(`| \`[x]\` | Được chứng minh bởi kiểm thử tự động đạt trong lần chạy này, hoặc kết quả thủ công đã ghi trong \`manual_results.csv\` |`);
  L.push(`| \`[ ]\` … _cần xác nhận thủ công_ | Không có kiểm thử tự động bao phủ; người kiểm thử phải làm và ghi nhận |`);
  L.push(`| \`[ ]\` … _chưa kiểm: … [TBD]_ | Ngưỡng hoặc cấu hình chưa chốt (OQ/AQ), chưa thể kết luận |`, "");

  L.push(`## 3. Checklist chung của lần chạy`, "");
  for (const l of LAYERS) {
    const s = src[l.file];
    L.push(s ? `- [${s.fail ? " " : "x"}] ${l.short}: ${s.pass}/${s.total} đạt${s.fail ? `, **${s.fail} lỗi**` : ""}${s.skip ? `, ${s.skip} bỏ qua` : ""}` : `- [ ] ${l.short}: không chạy`);
  }
  if (promtool) L.push(`- [${promtool === "SUCCESS" ? "x" : " "}] Luật cảnh báo (promtool): ${promtool}`);
  L.push(`- [${meta.dirty === false ? "x" : " "}] Mã ứng dụng không có thay đổi chưa commit khi chạy${meta.dirty === undefined ? " — _không rõ (thiếu run-meta.json)_" : meta.dirty ? " — **có thay đổi chưa commit**" : ""}`);
  L.push(`- [${missing.length ? " " : "x"}] Mọi ca có kiểm thử tự động đều tìm thấy kết quả${missing.length ? ` — còn ${missing.length}: ${missing.map((c) => c.id).join(", ")}` : ""}`);
  L.push(`- [${summary.unmapped_tests.length ? " " : "x"}] Mọi kiểm thử đều gắn với ca${summary.unmapped_tests.length ? ` — ${summary.unmapped_tests.length} chưa gắn (mục 6)` : ""}`);
  L.push(`- [${pending.length ? " " : "x"}] Ca thủ công đã ghi nhận${pending.length ? ` — còn ${pending.length} ca (mục 5)` : ""}`, "");

  L.push(`## 4. Ảnh kết quả`, "");
  L.push(`### 4.1 Ảnh kết quả từng ca`, "");
  L.push(`Mỗi ca có ảnh \`screenshots/ca/<Mã ca>.png\` (trạng thái, checklist, kiểm thử đã chạy với ✓/✗ và thời gian, căn cứ), nhúng đầu tiên trong mục **Ảnh kết quả** của ca trong tệp nhóm.`);
  L.push(`Ảnh dựng từ JUnit của lần chạy này. Với ca E2E/ACC/UI, ảnh giao diện thật đặt ngay sau.`, "");
  const sample = ["Đạt", "Không đạt", "Thủ công — chưa ghi nhận"].map((st) => caseData.find((c) => c.status === st && (st !== "Đạt" || c.tests.length > 1))).filter(Boolean);
  if (sample.length) {
    L.push(`| ${sample.map((c) => `${c.id} (${c.status})`).join(" | ")} |`, `|${sample.map(() => "---").join("|")}|`);
    L.push(`| ${sample.map((c) => `![](screenshots/ca/${c.id}.png)`).join(" | ")} |`, "");
  }
  L.push(`### 4.2 Kết quả từng tầng`, "", `Kết xuất từ tệp JUnit.`, "");
  for (const l of present) L.push(`**${l.label}**`, "", `[![${l.label}](screenshots/ket-qua/${l.file}.png)](screenshots/ket-qua/${l.file}.png)`, "");
  if (shotsByTitle.size) {
    L.push(`### 4.3 Ảnh giao diện thật`, "");
    L.push(`- [screenshots/e2e/](screenshots/e2e/): ảnh trạng thái cuối của ${shotsByTitle.size} ca E2E (${[...shotsByTitle.values()].flat().length} ảnh), tên \`<số ca>_<tệp spec>_<tên ca>_<n>.png\`. Ca mở thêm trang có nhiều ảnh; ảnh trùng của trang \`newPage()\` chưa đóng đã được loại.`);
    if (screens.length) {
      L.push(`- [screenshots/man-hinh/](screenshots/man-hinh/): màn hình S-01..S-07 do \`screenshots.spec.ts\` chụp.`, "");
      for (let i = 0; i < screens.length; i += 4) {
        const chunk = screens.slice(i, i + 4);
        L.push(`| ${chunk.map((s) => s.cap).join(" | ")} |`, `|${chunk.map(() => "---").join("|")}|`, `| ${chunk.map((s) => `![](${s.p})`).join(" | ")} |`, "");
      }
    } else L.push("");
  }

  L.push(`## 5. Ca còn chờ kiểm thử thủ công (${pending.length}${partials.length ? ` + ${partials.length} phần thủ công` : ""})`, "");
  if (pending.length || partials.length) {
    L.push(`Ghi kết quả vào [manual_results.csv](../manual_results.csv) (\`id,status,date,tester,note\`), rồi lập lại hồ sơ.`, "");
    L.push(`| Nhóm | Ca |`, `|---|---|`);
    for (const r of groupRows) {
      const ids = [...pending.filter((c) => c.group === r.g).map((c) => c.id), ...caseData.filter((c) => c.group === r.g && c.partial).map((c) => `${c.id} (phần thủ công)`)];
      if (ids.length) L.push(`| ${esc(r.gTitle.replace(/^\d+ — /, ""))} | ${ids.join(", ")} |`);
    }
    L.push("");
  } else L.push(`_Không có._`, "");
  if (ev) L.push(`Báo cáo bộ đánh giá mới nhất: \`${ev.file}\` — cấu hình: ${ev.config_note ?? "không ghi"}.${/hash|fake/i.test(ev.config_note ?? "") ? " Đây là kiểm chứng luồng, **không** dùng cho QE/LG-02..LG-05." : ""}`, "");

  L.push(`## 6. Kiểm thử chưa gắn với ca nào (${summary.unmapped_tests.length})`, "");
  L.push(summary.unmapped_tests.length ? `Đã chạy nhưng không ca nào trong \`docs/testing/test_cases\` tham chiếu tới; nên bổ sung truy vết.\n\n${summary.unmapped_tests.map((t) => `- ${esc(t)}`).join("\n")}` : "_Không có._", "");
  if (notes) L.push(`## 7. Ghi chú của người chạy`, "", notes, "");
  L.push(`## ${notes ? 8 : 7}. Cách chạy lại`, "", "```bash",
    `.claude/skills/test-run/scripts/run_layers.sh all          # hoặc từng tầng: frontend backend e2e eval alerts`,
    `node .claude/skills/test-run/scripts/build_run_docs.mjs --run ${RUN}`, "```", "");
  return L.join("\n");
}

// ---------- Checklist ----------
function buildChecklist(text, g, status, partial, manualCase) {
  const items = [];
  const section = (h) => (text.match(new RegExp(`\\*\\*${h}\\*\\*\\s*\\n([\\s\\S]*?)(?=\\n\\*\\*|\\n#|$)`)) ?? [])[1] ?? null;
  const exp = section("Kết quả mong đợi") ?? section("Tiêu chí chấp nhận");
  if (exp) for (const line of exp.split("\n")) {
    const b = line.match(/^\s*[-*]\s+(.*)$/) ?? line.match(/^\s*\d+\.\s+(.*)$/);
    if (b) items.push({ text: b[1].trim() });
    else if (/^\|/.test(line) && !/^\|\s*-/.test(line)) {
      const c = line.split("|").slice(1, -1).map((x) => x.trim());
      if (c.length >= 2 && !/^(Bước|Tương tác|Kiểm tra|Mục)$/i.test(c[0])) items.push({ text: `${c[0]}: ${c[1]}` });
    }
  }
  // Bảng "Tương tác | Kết quả mong đợi | Kiểm thử": dòng nào có tệp kiểm thử chạy đạt toàn bộ thì đánh dấu
  const inter = section("Các bước và kết quả mong đợi");
  if (inter) for (const line of inter.split("\n")) {
    const c = line.split("|").slice(1, -1).map((x) => x.trim());
    if (c.length < 3 || c[0] === "Tương tác" || /^-+$/.test(c[0])) continue;
    const manual = /thủ công/i.test(c[2]);
    const specs = [...c[2].matchAll(/`([^`]+\.(?:tsx?|py))`/g)].map((x) => path.basename(x[1]));
    const ts = tests.filter((t) => specs.includes(t.fileKey));
    const autoPass = !manual && specs.length > 0 && specs.every((sp) => ts.some((t) => t.fileKey === sp)) && ts.every((t) => t.status === "pass");
    items.push({ text: `${c[0]} → ${c[1]} _(${c[2]})_`, manual, autoPass });
  }
  if (g === "09_api") for (const k of ["Ra 200", "Ra 201", "Ra 202", "Ra 204", "Ra", "Lỗi"]) {
    const v = cell(text, k);
    if (v) items.push({ text: `${k}: ${v}` });
  }
  // Chỉ đánh dấu điều đã chứng minh: mục [TBD] và phần thủ công luôn để trống
  return items.map((c) => {
    const tbd = c.text.includes("[TBD");
    const mark = !tbd && !partial && (c.autoPass || (!c.manual && !manualCase && status === "Đạt"));
    const note = tbd ? " — _chưa kiểm: ngưỡng/cấu hình còn [TBD]_"
      : partial ? " — _phần tự động đạt, cần xác nhận thủ công_"
      : c.autoPass ? " — tệp kiểm thử đạt toàn bộ"
      : c.manual ? " — _cần xác nhận thủ công_" : "";
    return { text: c.text, note, mark };
  });
}

// ---------- Hàm phụ (cùng quy tắc khớp với collect_results.mjs) ----------
function parseRefs(cellText) {
  const refs = [];
  for (const seg of cellText.split(";")) {
    let file = null, fileRefs = 0;
    for (const m of seg.matchAll(/`([^`]+)`|"([^"]+)"/g)) {
      if (m[1]) {
        const tok = m[1].trim();
        if (tok.includes("*") || /\s/.test(tok)) continue;
        const [f, fn] = tok.split("::");
        if (/\.(py|tsx?|ya?ml)$/.test(f)) {
          if (file && fileRefs === 0) refs.push({ file });
          file = path.basename(f); fileRefs = 0;
          if (fn) { refs.push({ file, name: fn }); fileRefs++; }
        } else if (/^test_\w+$/.test(tok)) { refs.push({ file, name: tok }); fileRefs++; }
      } else if (m[2] && file && /\.tsx?$/.test(file)) { refs.push({ file, title: m[2] }); fileRefs++; }
    }
    if (file && fileRefs === 0) refs.push({ file });
  }
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
  const mod = cls.split(".").reverse().find((p) => p.startsWith("test_"));
  return mod ? `${mod}.py` : cls;
}
function latestRun() {
  const runs = fs.existsSync("test-results") ? fs.readdirSync("test-results").filter((d) => /^run-\d{4}-\d{2}-\d{2}/.test(d)).sort() : [];
  if (!runs.length) die("Không có test-results/run-*. Chạy run_layers.sh trước.");
  return runs.at(-1);
}
function cell(text, label) { const m = text.match(new RegExp(`^\\|\\s*${label}\\s*\\|(.*)\\|\\s*$`, "m")); return m ? m[1].trim() : null; }
function parseAttrs(s) { return Object.fromEntries([...s.matchAll(/([\w:-]+)="([^"]*)"/g)].map((m) => [m[1], m[2]])); }
function decode(s) { return s.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(n)).replace(/&#x([0-9a-f]+);/gi, (_, n) => String.fromCodePoint(parseInt(n, 16))).replace(/&amp;/g, "&"); }
function esc(s) { return String(s).replace(/\|/g, "\\|").replace(/\n/g, " "); }
function slug(s) { return s.replace(/[\\/:*?"<>|]/g, "").replace(/\s+/g, " ").trim().slice(0, 60); }
function dur(s) { s = Math.round(s); return s >= 60 ? `${Math.floor(s / 60)}m${String(s % 60).padStart(2, "0")}s` : `${s}s`; }
function countBy(arr, k) { return arr.reduce((o, x) => ((o[x[k]] = (o[x[k]] ?? 0) + 1), o), {}); }
function read(f) { return fs.readFileSync(f, "utf8"); }
function readJson(f) { return fs.existsSync(f) ? JSON.parse(read(f)) : null; }
function git(...a) { return execFileSync("git", a, { encoding: "utf8" }).trim(); }
function parseArgs(argv) {
  const o = {};
  for (let i = 0; i < argv.length; i++) if (argv[i].startsWith("--")) o[argv[i].slice(2)] = argv[i + 1]?.startsWith("--") || argv[i + 1] === undefined ? true : argv[++i];
  return o;
}
function die(msg) { console.error(msg); process.exit(1); }
