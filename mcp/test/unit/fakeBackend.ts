// Backend giả lập theo đúng hợp đồng /api/v1 mà MCP dùng: phiên cookie, kiểm Origin (CSRF), lỗi {"error"}.
// Ghi lại mọi yêu cầu để kiểm thử khẳng định header và thân gửi đi.

export interface Recorded {
  method: string;
  path: string;
  headers: Record<string, string>;
  body: unknown;
}

const ORIGIN = 'http://localhost:5173';
const DOC_A = '11111111-1111-4111-8111-111111111111';
const DOC_B = '22222222-2222-4222-8222-222222222222';
export const IDS = { DOC_A, DOC_B };

export function fakeBackend(opts: { role?: string; processingPolls?: number } = {}) {
  const calls: Recorded[] = [];
  const state = {
    sessions: new Set<string>(),
    sessionSeq: 0,
    conversations: [] as string[],
    expireNext: false,
    docs: [
      { id: DOC_A, file_name: 'HopDong_A.pdf', size_bytes: 120_000, page_count: 3, status: 'ready', failure_reason: null, uploaded_at: '2026-11-01T08:00:00Z' },
      { id: DOC_B, file_name: 'Hong.pdf', size_bytes: 900, page_count: null, status: 'failed', failure_reason: 'corrupted', uploaded_at: '2026-11-01T08:05:00Z' },
    ] as Record<string, unknown>[],
    pollsLeft: opts.processingPolls ?? 1,
    events: [] as unknown[],
    feedback: new Map<string, string>(),
  };

  const json = (status: number, body?: unknown, headers: Record<string, string> = {}) =>
    new Response(body === undefined ? null : JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', ...headers } });
  const err = (status: number, code: string, message: string) => json(status, { error: { code, message } });

  const fetchImpl = async (input: string | URL | Request, init: RequestInit = {}): Promise<Response> => {
    const url = new URL(String(input));
    const path = url.pathname.replace(/^\/api\/v1/, '') + url.search;
    const method = (init.method ?? 'GET').toUpperCase();
    const headers = Object.fromEntries(Object.entries((init.headers ?? {}) as Record<string, string>).map(([k, v]) => [k.toLowerCase(), v]));
    let body: unknown = init.body;
    if (typeof init.body === 'string') body = JSON.parse(init.body);
    calls.push({ method, path, headers, body });

    if (method !== 'GET' && headers.origin !== ORIGIN) return err(403, 'csrf_rejected', 'Yêu cầu bị từ chối vì không rõ nguồn gốc.');

    if (path === '/auth/login' && method === 'POST') {
      const b = body as { login: string; password: string };
      if (b.password !== 'dung') return err(401, 'invalid_credentials', 'Tên đăng nhập hoặc mật khẩu không đúng.');
      const token = `t${++state.sessionSeq}`;
      state.sessions.add(token);
      return json(200, {
        user: { id: '99999999-9999-4999-8999-999999999999', login: b.login, display_name: 'Nhân sự BD' },
        role: opts.role ?? 'bd',
        config: { max_file_bytes: 20 * 1024 * 1024, max_docs_per_user: 50, max_question_chars: 2000, poll_interval_s: 1, purge_sla_hours: 24, auth_mode: 'local' },
      }, { 'Set-Cookie': `cwd_session=${token}; HttpOnly; Path=/; SameSite=lax` });
    }

    const token = headers.cookie?.match(/cwd_session=([^;]+)/)?.[1];
    if (!token || !state.sessions.has(token)) return err(401, 'unauthenticated', 'Bạn cần đăng nhập để tiếp tục.');
    if (state.expireNext) {
      state.expireNext = false;
      state.sessions.delete(token);
      return err(401, 'session_expired', 'Phiên đăng nhập đã hết hạn. Hãy đăng nhập lại.');
    }
    const bdOnly = () => (opts.role ?? 'bd') !== 'bd' ? err(403, 'forbidden_role', 'Bạn không có quyền dùng chức năng này.') : null;

    if (path === '/auth/logout') { state.sessions.delete(token); return new Response(null, { status: 204 }); }
    if (path === '/documents' && method === 'GET') {
      const denied = bdOnly(); if (denied) return denied;
      for (const d of state.docs) if (d.status === 'processing') {
        if (state.pollsLeft-- <= 0) Object.assign(d, { status: 'ready', page_count: 2 });
      }
      return json(200, state.docs);
    }
    if (path === '/documents' && method === 'POST') {
      const form = init.body as FormData;
      const out = form.getAll('files').map((f, i) => {
        const file = f as File;
        const id = `33333333-3333-4333-8333-33333333333${i}`;
        state.docs.push({ id, file_name: file.name, size_bytes: file.size, page_count: null, status: 'processing', failure_reason: null, uploaded_at: '2026-11-02T08:00:00Z' });
        return { id, file_name: file.name, status: 'processing', failure_reason: null };
      });
      return json(200, out);
    }
    let m = path.match(/^\/documents\/([^/]+)$/);
    if (m) {
      const doc = state.docs.find((d) => d.id === m![1]);
      if (!doc) return err(404, 'document_not_found', 'Không tìm thấy tài liệu.');
      if (method === 'DELETE') { doc.status = 'deleting'; return json(202, { id: doc.id, status: 'deleting' }); }
      return json(200, doc);
    }
    m = path.match(/^\/documents\/([^/]+)\/pages\/(\d+)$/);
    if (m) {
      if (m[1] !== DOC_A) return err(404, 'document_not_found', 'Không đọc được tài liệu.');
      if (Number(m[2]) > 3) return err(404, 'page_not_found', 'Trang không tồn tại trong tài liệu.');
      return json(200, { page: Number(m[2]), page_count: 3, text: `Noi dung trang ${m[2]}: thanh toan trong 30 ngay.`, document_name: 'HopDong_A.pdf' });
    }
    if (path === '/events/source-opened') { state.events.push(body); return new Response(null, { status: 204 }); }
    if (path === '/conversations' && method === 'POST') {
      const denied = bdOnly(); if (denied) return denied;
      const id = `44444444-4444-4444-8444-44444444444${state.conversations.length}`;
      state.conversations.push(id);
      return json(201, { id });
    }
    m = path.match(/^\/conversations\/([^/]+)\/messages$/);
    if (m && method === 'POST') {
      const q = (body as { question: string }).question;
      if (/thu do/i.test(q)) return json(200, { message_id: '55555555-5555-4555-8555-555555555551', answer: '', not_found: true, citations: [], latency_ms: 12 });
      return json(200, {
        message_id: '55555555-5555-4555-8555-555555555550',
        answer: 'Thời hạn thanh toán là 30 ngày.',
        not_found: false,
        citations: [{ document_id: DOC_A, document_name: 'HopDong_A.pdf', page: 2, cited_text: 'thanh toan trong 30 ngay' }],
        latency_ms: 85,
      });
    }
    if (m && method === 'GET') {
      return json(200, [
        { id: 'm1', role: 'user', content: 'Thời hạn thanh toán?', not_found: false, latency_ms: null, created_at: '2026-11-02T08:00:00Z', citations: [], feedback: null },
        { id: 'm2', role: 'assistant', content: 'Thời hạn thanh toán là 30 ngày.', not_found: false, latency_ms: 85, created_at: '2026-11-02T08:00:01Z', citations: [{ document_id: DOC_A, document_name: 'HopDong_A.pdf', page: 2, cited_text: null }], feedback: 'helpful' },
      ]);
    }
    m = path.match(/^\/messages\/([^/]+)\/feedback$/);
    if (m) { state.feedback.set(m[1], (body as { value: string }).value); return new Response(null, { status: 204 }); }
    if (path.startsWith('/reports/usage')) {
      if ((opts.role ?? 'bd') !== 'manager') return err(403, 'forbidden_role', 'Bạn không có quyền dùng chức năng này.');
      return json(200, { weeks: [{ week: '2026-10-26', active_users: 7, questions: 42, helpful_ratio: 0.8, feedback_count: 10 }] });
    }
    return err(404, 'not_found', 'Không tìm thấy.');
  };

  return { fetch: fetchImpl as typeof fetch, calls, state };
}
