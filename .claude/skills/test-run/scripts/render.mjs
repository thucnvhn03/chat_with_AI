// Dựng ảnh PNG bằng Chromium của Playwright (lấy từ e2e/node_modules):
//   renderCases  — một ảnh/ca: trạng thái, checklist, kiểm thử đã chạy, căn cứ
//   renderLayers — một ảnh/tầng: danh sách kiểm thử trong tệp JUnit
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(path.resolve("e2e/package.json"));

const STATUS_STYLE = {
  "Đạt": ["#14532d", "#86efac", "ĐẠT"],
  "Không đạt": ["#7f1d1d", "#fca5a5", "KHÔNG ĐẠT"],
  "Bỏ qua": ["#422006", "#fcd34d", "BỎ QUA"],
  "Chưa có kết quả": ["#334155", "#cbd5e1", "CHƯA CÓ KẾT QUẢ"],
  "Thủ công — chưa ghi nhận": ["#1e3a8a", "#bfdbfe", "THỦ CÔNG — CHƯA GHI NHẬN"],
  "Bị chặn": ["#7c2d12", "#fdba74", "BỊ CHẶN"],
};
const ICON = { pass: "✓", fail: "✗", skip: "○" };

const BASE_CSS = `
body{margin:0;background:#0f172a;color:#e2e8f0;font:14px/1.5 "Segoe UI",sans-serif}
.pass{color:#4ade80}.fail{color:#f87171}.skip{color:#fbbf24}.dim{color:#64748b}`;

const CASE_CSS = `${BASE_CSS}
.card{width:960px;padding:22px 26px}
.top{display:flex;align-items:center;gap:12px}.id{font:700 20px Consolas,monospace;color:#7dd3fc}
.title{font-size:18px;font-weight:600}.badge{margin-left:auto;padding:5px 12px;border-radius:6px;font-weight:700;font-size:13px;white-space:nowrap}
.meta{color:#94a3b8;font-size:12.5px;margin:4px 0 14px}
h3{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:#94a3b8;margin:16px 0 6px}
.chk{display:flex;gap:10px;padding:3px 0}.box{flex:0 0 18px;height:18px;border-radius:4px;border:2px solid #64748b;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;margin-top:2px}
.box.on{background:#16a34a;border-color:#16a34a;color:#fff}
table{border-collapse:collapse;width:100%;font:12.5px Consolas,monospace}td{padding:3px 6px;border-bottom:1px solid #1e293b;vertical-align:top}
.msg{color:#fca5a5;font-size:11.5px}
.note{background:#1e293b;border-left:3px solid #f59e0b;padding:6px 10px;margin-top:8px;font-size:13px}
.foot{margin-top:16px;color:#475569;font-size:11.5px}`;

const LAYER_CSS = `${BASE_CSS}
body{font:13px/1.45 Consolas,monospace;padding:20px 24px}
h1{font:600 18px "Segoe UI",sans-serif;margin:0 0 4px}.sub{color:#94a3b8;margin-bottom:14px;font-family:"Segoe UI",sans-serif}
.sum{display:flex;gap:10px;margin-bottom:16px}.b{padding:6px 12px;border-radius:6px;font:600 14px "Segoe UI",sans-serif}
.p{background:#14532d;color:#86efac}.f{background:#7f1d1d;color:#fca5a5}.s{background:#422006;color:#fcd34d}
.file{color:#7dd3fc;margin-top:10px;font-weight:600}.row{display:flex;gap:8px;padding-left:14px}
.t{color:#64748b;margin-left:auto;white-space:nowrap}.n{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}`;

async function withPage(width, fn) {
  const { chromium } = require("@playwright/test");
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({ viewport: { width, height: 400 } });
    await fn(page);
  } finally {
    await browser.close();
  }
}

/** cases: [{id, title, group, priority, status, partial, checklist:[{mark,text}], tests:[...], evidence:[], extra}] */
export async function renderCases(cases, outDir, { runLabel, commit }) {
  fs.mkdirSync(outDir, { recursive: true });
  await withPage(1012, async (page) => {
    for (const c of cases) {
      const [bg, fg, label] = STATUS_STYLE[c.status] ?? STATUS_STYLE["Chưa có kết quả"];
      const pass = c.tests.filter((t) => t.status === "pass").length;
      const done = c.checklist.filter((x) => x.mark).length;
      const html = `<!doctype html><meta charset="utf-8"><style>${CASE_CSS}</style><div class="card" id="card">
      <div class="top"><span class="id">${c.id}</span><span class="title">${esc(c.title)}</span>
      <span class="badge" style="background:${bg};color:${fg}">${label}${c.partial ? " (TỰ ĐỘNG)" : ""}</span></div>
      <div class="meta">Nhóm ${c.group}${c.priority ? ` · Ưu tiên ${esc(c.priority)}` : ""} · ${esc(runLabel)} · commit ${esc(commit)}
      · Checklist ${done}/${c.checklist.length}${c.tests.length ? ` · Kiểm thử tự động ${pass}/${c.tests.length} đạt` : ""}</div>
      <h3>Checklist kết quả mong đợi</h3>
      ${c.checklist.length
        ? c.checklist.map((x) => `<div class="chk"><span class="box ${x.mark ? "on" : ""}">${x.mark ? "✓" : ""}</span><span>${esc(x.text)}</span></div>`).join("")
        : `<div class="dim">(đặc tả không có danh sách kết quả mong đợi)</div>`}
      ${c.tests.length ? `<h3>Kiểm thử tự động đã chạy</h3><table>${c.tests.map((t) =>
        `<tr><td class="${t.status}">${ICON[t.status]}</td><td class="dim">${t.layer}</td><td style="color:#7dd3fc">${esc(t.file)}</td><td>${esc(t.name)}${t.message ? `<div class="msg">${esc(t.message)}</div>` : ""}</td><td class="dim" style="text-align:right;white-space:nowrap">${t.time.toFixed(2)}s</td></tr>`).join("")}</table>` : ""}
      ${c.evidence.length ? `<h3>Căn cứ</h3><div>${c.evidence.map(esc).join("<br>")}</div>` : ""}
      ${c.extra ? `<h3>Bằng chứng khác</h3><div>${esc(c.extra)}</div>` : ""}
      ${c.missing?.length ? `<div class="note">Không tìm thấy kết quả cho: ${esc(c.missing.join(", "))} — tầng kiểm thử chưa chạy trong lần này, hoặc tên kiểm thử trong đặc tả đã cũ</div>` : ""}
      ${c.partial ? `<div class="note">Phần tự động đạt — phần thủ công chưa ghi nhận trong manual_results.csv</div>` : ""}
      ${/Thủ công/.test(c.status) ? `<div class="note">Ca thủ công: chưa có kết quả ghi nhận. Cần thực hiện theo đặc tả và ghi vào docs/testing/results/manual_results.csv</div>` : ""}
      <div class="foot">Nguồn: JUnit XML (pytest / Vitest / Playwright) · ${esc(runLabel)}</div></div>`;
      await page.setContent(html);
      await page.locator("#card").screenshot({ path: path.join(outDir, `${c.id}.png`) });
    }
  });
}

/** layers: [{label, file (JUnit XML), slug}] */
export async function renderLayers(layers, outDir, { runLabel }) {
  fs.mkdirSync(outDir, { recursive: true });
  await withPage(1100, async (page) => {
    for (const { label, file, slug } of layers) {
      const byFile = new Map();
      let pass = 0, fail = 0, skip = 0, secs = 0;
      for (const t of readJunit(file)) {
        t.status === "pass" ? pass++ : t.status === "fail" ? fail++ : skip++;
        secs += t.time;
        if (!byFile.has(t.group)) byFile.set(t.group, []);
        byFile.get(t.group).push(t);
      }
      const html = `<!doctype html><meta charset="utf-8"><style>${LAYER_CSS}</style>
      <h1>${esc(label)}</h1><div class="sub">${path.basename(file)} · ${esc(runLabel)}</div>
      <div class="sum"><span class="b p">${pass} đạt</span><span class="b f">${fail} lỗi</span><span class="b s">${skip} bỏ qua</span><span class="b" style="background:#1e293b">${Math.round(secs)} s</span></div>
      ${[...byFile].map(([f, ts]) => `<div class="file">${esc(f)} (${ts.length})</div>` + ts.map((t) =>
        `<div class="row"><span class="${t.status}">${ICON[t.status]}</span><span class="n">${esc(t.name)}</span><span class="t">${t.time.toFixed(2)}s</span></div>`).join("")).join("")}`;
      await page.setContent(html);
      await page.screenshot({ path: path.join(outDir, `${slug}.png`), fullPage: true });
    }
  });
}

function readJunit(file) {
  const xml = fs.readFileSync(file, "utf8");
  return [...xml.matchAll(/<testcase\b([^>]*?)(\/>|>([\s\S]*?)<\/testcase>)/g)].map((m) => {
    const a = Object.fromEntries([...m[1].matchAll(/([\w:-]+)="([^"]*)"/g)].map((x) => [x[1], decode(x[2])]));
    const body = m[3] ?? "";
    return {
      group: a.file ?? a.classname, name: a.name, time: Number(a.time ?? 0),
      status: /<(failure|error)\b/.test(body) ? "fail" : /<skipped\b/.test(body) ? "skip" : "pass",
    };
  });
}
function decode(s) { return s.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(n)).replace(/&amp;/g, "&"); }
function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;"); }
