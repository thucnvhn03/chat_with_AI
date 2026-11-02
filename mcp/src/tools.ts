// Tool MCP: dùng "Chat với tài liệu" từ Claude với quyền của chính tài khoản đã cấu hình.
// Mọi kiểm quyền, cô lập tài liệu, kiểm toán vẫn do backend làm; MCP chỉ là một client như giao diện web.
// Không ghi nội dung câu hỏi/câu trả lời ra log (cùng nguyên tắc với backend).
import { readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import type { CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { ApiError, type ApiClient, type Citation, type DocumentInfo } from './client.js';

// Cùng câu chữ với frontend/src/features/documents/failureMessages.ts (US-004, AC-018)
const FAILURE_MESSAGES: Record<string, string> = {
  corrupted: 'Tệp bị hỏng hoặc không đọc được. Hãy mở thử tệp trên máy, lưu lại bản PDF mới rồi tải lại.',
  encrypted: 'Tài liệu bị khóa hoặc mã hóa. Hãy mở khóa rồi tải lại.',
  not_pdf: 'Tệp không phải PDF. Hãy chuyển tài liệu sang định dạng PDF rồi tải lại.',
  too_large: 'Tệp vượt quá dung lượng cho phép. Hãy tách hoặc nén tài liệu rồi tải lại.',
  no_text:
    'Tài liệu không có văn bản đọc được (có thể là bản scan dạng ảnh). Hiện chưa hỗ trợ loại tệp này; hãy dùng bản PDF có văn bản.',
  network: 'Mất kết nối khi tải lên. Tệp chưa nằm trong tập tài liệu; hãy tải lại khi có mạng.',
  internal: 'Hệ thống chưa xử lý được tệp này. Hãy thử lại sau ít phút.',
  too_many_documents: 'Bạn đã đạt số lượng tài liệu tối đa. Hãy xóa bớt tài liệu không dùng rồi tải lại.',
};
const GENERIC_FAILURE = 'Không xử lý được tệp này. Hãy thử lại; nếu vẫn lỗi, hãy liên hệ bộ phận hỗ trợ.';

const STATUS_LABEL: Record<string, string> = {
  uploading: 'Đang tải lên',
  processing: 'Đang xử lý',
  ready: 'Sẵn sàng',
  failed: 'Lỗi',
  deleting: 'Đang xóa',
  deleted: 'Đã xóa',
};
const PENDING = new Set(['uploading', 'processing']);

export interface ToolDeps {
  readFile: (p: string) => Promise<Uint8Array>;
  fileSize: (p: string) => Promise<number>;
  sleep: (ms: number) => Promise<void>;
  uploadWaitSeconds: number;
}

const defaultDeps: ToolDeps = {
  readFile: (p) => readFile(p),
  fileSize: async (p) => (await stat(p)).size,
  sleep: (ms) => new Promise((r) => setTimeout(r, ms)),
  uploadWaitSeconds: 180,
};

const uuid = z.string().uuid();

export function registerTools(server: McpServer, api: ApiClient, deps: Partial<ToolDeps> = {}): void {
  const d = { ...defaultDeps, ...deps };
  // Hội thoại hiện tại của tiến trình MCP: câu hỏi tiếp theo ("còn hợp đồng B thì sao?") dùng chung ngữ cảnh
  let currentConversation: string | null = null;

  server.registerTool(
    'whoami',
    {
      title: 'Tài khoản đang dùng',
      description: 'Cho biết tài khoản, vai trò (bd / manager / security_admin) và các giới hạn của hệ thống "Chat với tài liệu".',
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    () =>
      run(async () => {
        const me = await api.session();
        const c = me.config;
        return [
          `Tài khoản: ${me.user.display_name && me.user.display_name !== me.user.login ? `${me.user.display_name} (${me.user.login})` : me.user.login}`,
          `Vai trò: ${roleLabel(me.role)}`,
          `Giới hạn: tệp tối đa ${mb(c.max_file_bytes)}, tối đa ${c.max_docs_per_user} tài liệu, câu hỏi tối đa ${c.max_question_chars} ký tự.`,
          `Tài liệu xóa sẽ bị xóa vĩnh viễn trong ${c.purge_sla_hours} giờ.`,
        ].join('\n');
      }),
  );

  server.registerTool(
    'list_documents',
    {
      title: 'Danh sách tài liệu',
      description:
        'Liệt kê tài liệu PDF của người dùng: tên, số trang, dung lượng, trạng thái (Sẵn sàng / Đang xử lý / Lỗi kèm lý do) và id. Chỉ tài liệu "Sẵn sàng" được dùng để trả lời câu hỏi.',
      inputSchema: {
        status: z.enum(['ready', 'processing', 'failed']).optional().describe('Chỉ lấy tài liệu ở trạng thái này'),
      },
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    ({ status }) =>
      run(async () => {
        let docs = await api.listDocuments();
        if (status) docs = docs.filter((x) => (status === 'processing' ? PENDING.has(x.status) : x.status === status));
        if (!docs.length) return status ? `Không có tài liệu nào ở trạng thái "${STATUS_LABEL[status]}".` : 'Chưa có tài liệu nào. Dùng upload_documents để tải PDF lên.';
        const ready = docs.filter((x) => x.status === 'ready').length;
        return [`${docs.length} tài liệu (${ready} sẵn sàng):`, ...docs.map(docLine)].join('\n');
      }),
  );

  server.registerTool(
    'upload_documents',
    {
      title: 'Tải PDF lên',
      description:
        'Tải một hoặc nhiều tệp PDF trên máy lên tập tài liệu của người dùng. Mặc định chờ tới khi xử lý xong và báo trạng thái từng tệp (Sẵn sàng, hoặc Lỗi kèm cách khắc phục). Chỉ nhận tệp .pdf.',
      inputSchema: {
        paths: z.array(z.string().min(1)).min(1).max(20).describe('Đường dẫn tệp PDF (tuyệt đối, hoặc tương đối với thư mục làm việc của MCP server)'),
        wait: z.boolean().default(true).describe('Chờ xử lý xong (mặc định true)'),
      },
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: false },
    },
    ({ paths, wait }) =>
      run(async () => {
        const me = await api.session();
        const lines: string[] = [];
        const files: { name: string; data: Uint8Array }[] = [];
        for (const p of paths) {
          const full = path.resolve(p);
          const name = path.basename(full);
          // Kiểm sớm ở máy người dùng để không gửi tệp chắc chắn bị từ chối; backend vẫn kiểm lại
          if (!/\.pdf$/i.test(name)) { lines.push(`✗ ${name}: ${FAILURE_MESSAGES.not_pdf}`); continue; }
          let size: number;
          try { size = await d.fileSize(full); } catch { lines.push(`✗ ${name}: không tìm thấy tệp ${full}`); continue; }
          if (size > me.config.max_file_bytes) { lines.push(`✗ ${name}: ${FAILURE_MESSAGES.too_large} (${mb(size)} > ${mb(me.config.max_file_bytes)})`); continue; }
          const data = await d.readFile(full);
          if (Buffer.from(data.subarray(0, 5)).toString('latin1') !== '%PDF-') { lines.push(`✗ ${name}: ${FAILURE_MESSAGES.not_pdf}`); continue; }
          files.push({ name, data });
        }
        if (!files.length) return { text: lines.join('\n'), isError: true };

        const results = await api.uploadDocuments(files);
        let docs: (DocumentInfo | { id: string | null; file_name: string; status: string; failure_reason: string | null; page_count?: null })[] = results;
        if (wait) {
          const ids = results.filter((r) => r.id && PENDING.has(r.status)).map((r) => r.id!);
          const final = await waitUntilProcessed(api, ids, me.config.poll_interval_s, d);
          docs = results.map((r) => (r.id && final.has(r.id) ? final.get(r.id)! : r));
        }
        for (const x of docs) {
          if (x.status === 'ready') lines.push(`✓ ${x.file_name}: Sẵn sàng${x.page_count ? `, ${x.page_count} trang` : ''} (id ${x.id})`);
          else if (PENDING.has(x.status)) lines.push(`… ${x.file_name}: ${STATUS_LABEL[x.status]} (id ${x.id})${wait ? ' — chưa xong sau thời gian chờ; kiểm lại bằng list_documents' : ''}`);
          else lines.push(`✗ ${x.file_name}: ${failure(x.failure_reason)}${x.id ? ` (id ${x.id}; có thể dùng retry_document)` : ''}`);
        }
        return lines.join('\n');
      }),
  );

  server.registerTool(
    'retry_document',
    {
      title: 'Thử xử lý lại tài liệu lỗi',
      description: 'Đưa tài liệu đang ở trạng thái Lỗi vào xử lý lại (ví dụ sau lỗi tạm thời của hệ thống).',
      inputSchema: { document_id: uuid.describe('id tài liệu (từ list_documents)') },
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: false },
    },
    ({ document_id }) =>
      run(async () => {
        const doc = await api.retryDocument(document_id);
        return `Đã đưa "${doc.file_name}" vào xử lý lại: ${STATUS_LABEL[doc.status] ?? doc.status}.`;
      }),
  );

  server.registerTool(
    'delete_document',
    {
      title: 'Xóa tài liệu vĩnh viễn',
      description:
        'XÓA VĨNH VIỄN một tài liệu: ngừng dùng để trả lời ngay, tệp và dữ liệu bị xóa hẳn, không thể khôi phục. Chỉ gọi khi người dùng đã xác nhận rõ tên tài liệu cần xóa.',
      inputSchema: {
        document_id: uuid.describe('id tài liệu (từ list_documents)'),
        confirm_file_name: z.string().min(1).describe('Tên tệp chính xác của tài liệu, để tránh xóa nhầm'),
      },
      annotations: { readOnlyHint: false, destructiveHint: true, idempotentHint: true, openWorldHint: false },
    },
    ({ document_id, confirm_file_name }) =>
      run(async () => {
        const doc = await api.getDocument(document_id);
        if (doc.file_name !== confirm_file_name) {
          return { text: `Không xóa: tài liệu ${document_id} có tên "${doc.file_name}", không khớp "${confirm_file_name}".`, isError: true };
        }
        await api.deleteDocument(document_id);
        const me = await api.session();
        return `Đã xóa "${doc.file_name}". Tài liệu không còn được dùng để trả lời; dữ liệu sẽ bị xóa vĩnh viễn trong ${me.config.purge_sla_hours} giờ.`;
      }),
  );

  server.registerTool(
    'ask',
    {
      title: 'Hỏi đáp trên tài liệu',
      description:
        'Hỏi một câu về nội dung các tài liệu "Sẵn sàng" của người dùng. Câu trả lời CHỈ dựa trên tài liệu và kèm nguồn (tên tệp, số trang). ' +
        'Câu hỏi tiếp theo dùng chung hội thoại nên hỏi tiếp được ("còn hợp đồng B thì sao?"). ' +
        'Nếu kết quả là "không tìm thấy", hãy nói đúng như vậy với người dùng — không tự trả lời bằng kiến thức chung. Khi nhắc lại câu trả lời, giữ nguyên các nguồn.',
      inputSchema: {
        question: z.string().min(1).describe('Câu hỏi bằng ngôn ngữ tự nhiên'),
        new_conversation: z.boolean().default(false).describe('Bắt đầu hội thoại mới, không mang ngữ cảnh câu trước'),
        conversation_id: uuid.optional().describe('Tiếp tục một hội thoại cụ thể thay vì hội thoại hiện tại'),
      },
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: false },
    },
    ({ question, new_conversation, conversation_id }) =>
      run(async () => {
        if (conversation_id) currentConversation = conversation_id;
        else if (new_conversation || !currentConversation) currentConversation = await api.createConversation();
        const a = await api.ask(currentConversation, question);
        const lines = a.not_found
          ? [`KHÔNG TÌM THẤY thông tin này trong các tài liệu đã tải lên.`, a.answer && a.answer !== '' ? a.answer : 'Có thể bổ sung tài liệu liên quan hoặc đổi cách đặt câu hỏi.']
          : [a.answer, '', formatCitations(a.citations)];
        lines.push('', `(conversation_id ${currentConversation} · message_id ${a.message_id} · ${a.latency_ms} ms)`);
        return lines.join('\n');
      }),
  );

  server.registerTool(
    'new_conversation',
    {
      title: 'Hội thoại mới',
      description: 'Bắt đầu hội thoại mới; câu hỏi sau không mang ngữ cảnh của các câu trước.',
      annotations: { readOnlyHint: false, destructiveHint: false, openWorldHint: false },
    },
    () =>
      run(async () => {
        currentConversation = await api.createConversation();
        return `Đã bắt đầu hội thoại mới (conversation_id ${currentConversation}).`;
      }),
  );

  server.registerTool(
    'get_conversation',
    {
      title: 'Lịch sử hội thoại',
      description: 'Xem các câu hỏi và câu trả lời (kèm nguồn) của hội thoại hiện tại hoặc một hội thoại theo id.',
      inputSchema: { conversation_id: uuid.optional().describe('Mặc định: hội thoại hiện tại') },
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    ({ conversation_id }) =>
      run(async () => {
        const id = conversation_id ?? currentConversation;
        if (!id) return 'Chưa có hội thoại nào trong phiên này. Dùng ask để đặt câu hỏi.';
        const msgs = await api.listMessages(id);
        if (!msgs.length) return `Hội thoại ${id} chưa có câu hỏi nào.`;
        return msgs
          .map((m) =>
            m.role === 'user'
              ? `Hỏi: ${m.content}`
              : `Đáp${m.not_found ? ' (không tìm thấy)' : ''}: ${m.content}${m.citations.length ? `\n${formatCitations(m.citations)}` : ''}\n(message_id ${m.id}${m.feedback ? `, đánh giá: ${m.feedback}` : ''})`,
          )
          .join('\n\n');
      }),
  );

  server.registerTool(
    'get_source_page',
    {
      title: 'Đọc trang nguồn',
      description: 'Đọc văn bản của một trang trong tài liệu — dùng để kiểm tra nguồn được trích trong câu trả lời.',
      inputSchema: {
        document_id: uuid.describe('id tài liệu (từ nguồn của câu trả lời hoặc list_documents)'),
        page: z.number().int().min(1).describe('Số trang, bắt đầu từ 1'),
      },
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    ({ document_id, page }) =>
      run(async () => {
        const p = await api.getPage(document_id, page);
        // Ghi sự kiện "mở nguồn" như giao diện web; lỗi ghi sự kiện không chặn việc đọc trang
        await api.sourceOpened(document_id, page).catch(() => undefined);
        return `${p.document_name} — trang ${p.page}/${p.page_count}\n\n${p.text}`;
      }),
  );

  server.registerTool(
    'send_feedback',
    {
      title: 'Đánh giá câu trả lời',
      description: 'Ghi đánh giá Hữu ích / Không hữu ích cho một câu trả lời (theo message_id). Chỉ gọi khi người dùng thực sự đánh giá.',
      inputSchema: {
        message_id: uuid.describe('message_id của câu trả lời (từ ask)'),
        value: z.enum(['helpful', 'not_helpful']),
      },
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: false },
    },
    ({ message_id, value }) =>
      run(async () => {
        await api.setFeedback(message_id, value);
        return `Đã ghi đánh giá: ${value === 'helpful' ? 'Hữu ích' : 'Không hữu ích'}.`;
      }),
  );

  server.registerTool(
    'usage_report',
    {
      title: 'Báo cáo mức sử dụng',
      description: 'Báo cáo theo tuần: số người dùng hoạt động, số câu hỏi, tỷ lệ đánh giá hữu ích. Chỉ dành cho vai trò quản lý (manager).',
      inputSchema: { weeks: z.number().int().min(1).max(52).default(4).describe('Số tuần gần nhất') },
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    ({ weeks }) =>
      run(async () => {
        const rows = await api.usage(weeks);
        if (!rows.length) return 'Chưa có số liệu sử dụng.';
        return [
          '| Tuần (từ thứ Hai) | Người dùng hoạt động | Câu hỏi | Tỷ lệ hữu ích | Số đánh giá |',
          '|---|---|---|---|---|',
          ...rows.map((w) => `| ${w.week} | ${w.active_users} | ${w.questions} | ${w.helpful_ratio == null ? '—' : `${Math.round(w.helpful_ratio * 100)}%`} | ${w.feedback_count} |`),
        ].join('\n');
      }),
  );
}

async function waitUntilProcessed(api: ApiClient, ids: string[], pollSeconds: number, d: ToolDeps): Promise<Map<string, DocumentInfo>> {
  const out = new Map<string, DocumentInfo>();
  const deadline = Date.now() + d.uploadWaitSeconds * 1000;
  let pending = [...ids];
  while (pending.length && Date.now() < deadline) {
    await d.sleep(Math.max(1, pollSeconds) * 1000);
    const docs = await api.listDocuments();
    for (const doc of docs) if (pending.includes(doc.id)) out.set(doc.id, doc);
    pending = pending.filter((id) => !out.has(id) || PENDING.has(out.get(id)!.status));
  }
  return out;
}

/** Bọc xử lý tool: chuyển lỗi backend thành kết quả lỗi đọc được, không ném ra ngoài. */
async function run(fn: () => Promise<string | { text: string; isError: boolean }>): Promise<CallToolResult> {
  try {
    const r = await fn();
    return typeof r === 'string' ? { content: [{ type: 'text', text: r }] } : { content: [{ type: 'text', text: r.text }], isError: r.isError };
  } catch (e) {
    return { content: [{ type: 'text', text: errorText(e) }], isError: true };
  }
}

function errorText(e: unknown): string {
  if (e instanceof ApiError) {
    const hint: Record<string, string> = {
      invalid_credentials: ' Kiểm tra CWD_LOGIN / CWD_PASSWORD trong cấu hình MCP.',
      csrf_rejected: ' Đặt CWD_ORIGIN thành một giá trị trong ALLOWED_ORIGINS của backend.',
      forbidden_role: ' Tài khoản hiện tại không có vai trò dùng được chức năng này.',
    };
    return `${e.message} [${e.code}]${hint[e.code] ?? ''}`;
  }
  const cause = (e as { cause?: { code?: string } })?.cause?.code;
  if (cause === 'ECONNREFUSED') return 'Không kết nối được backend. Kiểm tra hệ thống đã chạy và CWD_API_URL đúng.';
  return `Lỗi: ${(e as Error)?.message ?? String(e)}`;
}

function formatCitations(cs: Citation[]): string {
  if (!cs.length) return 'Nguồn: (không có)';
  return ['Nguồn:', ...cs.map((c, i) => `[${i + 1}] ${c.document_name}, tr. ${c.page}${c.cited_text ? ` — "${oneLine(c.cited_text, 160)}"` : ''} (document_id ${c.document_id})`)].join('\n');
}

function docLine(x: DocumentInfo): string {
  const parts = [STATUS_LABEL[x.status] ?? x.status, x.page_count ? `${x.page_count} trang` : null, mb(x.size_bytes)].filter(Boolean);
  const reason = x.status === 'failed' ? ` — ${failure(x.failure_reason)}` : '';
  return `- ${x.file_name} · ${parts.join(' · ')}${reason} (id ${x.id})`;
}

function failure(code: string | null | undefined): string {
  return code && Object.prototype.hasOwnProperty.call(FAILURE_MESSAGES, code) ? FAILURE_MESSAGES[code] : GENERIC_FAILURE;
}
function roleLabel(r: string): string {
  return { bd: 'Nhân sự BD (hỏi đáp tài liệu)', manager: 'Quản lý (báo cáo sử dụng)', security_admin: 'Quản trị bảo mật' }[r] ?? r;
}
function mb(bytes: number): string {
  return bytes >= 1024 * 1024 ? `${(bytes / 1024 / 1024).toFixed(1)} MB` : bytes >= 1024 ? `${Math.round(bytes / 1024)} KB` : `${bytes} B`;
}
function oneLine(s: string, max: number): string {
  const t = s.replace(/\s+/g, ' ').trim();
  return t.length > max ? `${t.slice(0, max - 1)}…` : t;
}
