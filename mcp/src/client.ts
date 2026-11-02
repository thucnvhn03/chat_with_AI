// Client HTTP tối giản cho API backend /api/v1 (implement_plan.md mục 4).
// - Phiên: cookie `cwd_session` lấy từ POST /auth/login; tự đăng nhập lại một lần khi phiên hết hạn.
// - CSRF: yêu cầu thay đổi dữ liệu gửi kèm header Origin (backend app/api/security.py).
// - Lỗi: backend trả {"error": {"code", "message"}} → ApiError giữ nguyên mã và thông điệp tiếng Việt.
import type { Config } from './config.js';

export interface ClientConfig {
  max_file_bytes: number;
  max_docs_per_user: number;
  max_question_chars: number;
  poll_interval_s: number;
  purge_sla_hours: number;
  auth_mode: string;
}

export interface Me {
  user: { id: string; login: string; display_name: string | null };
  role: 'bd' | 'manager' | 'security_admin' | string;
  config: ClientConfig;
}

export interface DocumentInfo {
  id: string;
  file_name: string;
  size_bytes: number;
  page_count: number | null;
  status: 'uploading' | 'processing' | 'ready' | 'failed' | 'deleting' | 'deleted' | string;
  failure_reason: string | null;
  uploaded_at: string;
}

export interface UploadResult {
  id: string | null;
  file_name: string;
  status: string;
  failure_reason: string | null;
}

export interface Citation {
  document_id: string;
  document_name: string;
  page: number;
  cited_text: string | null;
}

export interface Answer {
  message_id: string;
  answer: string;
  not_found: boolean;
  citations: Citation[];
  latency_ms: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | string;
  content: string;
  not_found: boolean;
  latency_ms: number | null;
  created_at: string;
  citations: Citation[];
  feedback: string | null;
}

export interface Page {
  page: number;
  page_count: number;
  text: string;
  document_name: string;
}

export interface UsageWeek {
  week: string;
  active_users: number;
  questions: number;
  helpful_ratio: number | null;
  feedback_count: number;
}

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(message);
  }
}

type Fetch = typeof fetch;
const SESSION_EXPIRED = new Set(['unauthenticated', 'session_expired']);

export class ApiClient {
  private cookie: string | null = null;
  private me: Me | null = null;

  constructor(
    private readonly config: Config,
    private readonly fetchImpl: Fetch = fetch,
  ) {}

  /** Đăng nhập (nếu chưa) và trả thông tin phiên: người dùng, vai trò, giới hạn. */
  async session(): Promise<Me> {
    if (!this.me) await this.login();
    return this.me!;
  }

  async login(): Promise<Me> {
    const res = await this.fetchImpl(`${this.config.apiUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Origin: this.config.origin },
      body: JSON.stringify({ login: this.config.login, password: this.config.password }),
    });
    if (!res.ok) throw await toApiError(res);
    const cookie = sessionCookie(res);
    if (!cookie) throw new ApiError(res.status, 'no_session_cookie', 'Backend không trả cookie phiên sau khi đăng nhập.');
    this.cookie = cookie;
    this.me = (await res.json()) as Me;
    return this.me;
  }

  async logout(): Promise<void> {
    if (!this.cookie) return;
    await this.request('POST', '/auth/logout', undefined, { retry: false });
    this.cookie = null;
    this.me = null;
  }

  listDocuments(): Promise<DocumentInfo[]> {
    return this.request('GET', '/documents');
  }

  getDocument(id: string): Promise<DocumentInfo> {
    return this.request('GET', `/documents/${enc(id)}`);
  }

  retryDocument(id: string): Promise<DocumentInfo> {
    return this.request('POST', `/documents/${enc(id)}/retry`);
  }

  deleteDocument(id: string): Promise<{ id: string; status: string }> {
    return this.request('DELETE', `/documents/${enc(id)}`);
  }

  uploadDocuments(files: { name: string; data: Uint8Array }[]): Promise<UploadResult[]> {
    return this.request('POST', '/documents', () => {
      const form = new FormData();
      for (const f of files) form.append('files', new Blob([f.data], { type: 'application/pdf' }), f.name);
      return form;
    });
  }

  async createConversation(): Promise<string> {
    const out = await this.request<{ id: string }>('POST', '/conversations');
    return out.id;
  }

  ask(conversationId: string, question: string): Promise<Answer> {
    return this.request('POST', `/conversations/${enc(conversationId)}/messages`, { question });
  }

  listMessages(conversationId: string): Promise<Message[]> {
    return this.request('GET', `/conversations/${enc(conversationId)}/messages`);
  }

  setFeedback(messageId: string, value: 'helpful' | 'not_helpful'): Promise<void> {
    return this.request('PUT', `/messages/${enc(messageId)}/feedback`, { value });
  }

  getPage(documentId: string, page: number): Promise<Page> {
    return this.request('GET', `/documents/${enc(documentId)}/pages/${page}`);
  }

  /** Sự kiện phân tích "mở nguồn" (T2-11) — giống giao diện web khi người dùng mở một trang nguồn. */
  sourceOpened(documentId: string, page: number): Promise<void> {
    return this.request('POST', '/events/source-opened', { document_id: documentId, page });
  }

  async usage(weeks: number): Promise<UsageWeek[]> {
    const out = await this.request<{ weeks: UsageWeek[] }>('GET', `/reports/usage?weeks=${weeks}`);
    return out.weeks;
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown | (() => FormData),
    { retry = true }: { retry?: boolean } = {},
  ): Promise<T> {
    if (!this.cookie) await this.login();
    const headers: Record<string, string> = { Cookie: this.cookie! };
    if (method !== 'GET') headers.Origin = this.config.origin;
    let payload: FormData | string | undefined;
    if (typeof body === 'function') payload = (body as () => FormData)();
    else if (body !== undefined) {
      headers['Content-Type'] = 'application/json';
      payload = JSON.stringify(body);
    }
    const res = await this.fetchImpl(`${this.config.apiUrl}${path}`, { method, headers, body: payload });
    if (!res.ok) {
      const err = await toApiError(res);
      if (retry && res.status === 401 && SESSION_EXPIRED.has(err.code)) {
        this.cookie = null;
        this.me = null;
        return this.request(method, path, body, { retry: false });
      }
      throw err;
    }
    if (res.status === 204) return undefined as T;
    return (await res.json()) as T;
  }
}

async function toApiError(res: Response): Promise<ApiError> {
  let code = `http_${res.status}`;
  let message = `Backend trả HTTP ${res.status}.`;
  try {
    const data = (await res.json()) as { error?: { code?: string; message?: string }; detail?: unknown };
    if (data.error?.code) code = data.error.code;
    if (data.error?.message) message = data.error.message;
    else if (data.detail) message = `Dữ liệu gửi lên không hợp lệ: ${JSON.stringify(data.detail).slice(0, 300)}`;
  } catch {
    // Thân không phải JSON (proxy, lỗi mạng) — giữ thông điệp chung
  }
  return new ApiError(res.status, code, message);
}

function sessionCookie(res: Response): string | null {
  const all = typeof res.headers.getSetCookie === 'function' ? res.headers.getSetCookie() : [res.headers.get('set-cookie') ?? ''];
  for (const c of all) {
    const pair = c.split(';')[0]?.trim();
    if (pair?.startsWith('cwd_session=')) return pair;
  }
  return null;
}

function enc(id: string): string {
  return encodeURIComponent(id);
}
