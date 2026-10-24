// Client gọi backend (/api/v1). Kiểu dữ liệu sinh từ OpenAPI của backend: `npm run gen:api`.
// Lỗi luôn có dạng {"error": {"code", "message"}}; 401 báo cho AuthGate để quay về màn hình đăng nhập.
import type { components } from './schema';

export type Schemas = components['schemas'];
export type Me = Schemas['MeOut'];
export type DocumentOut = Schemas['DocumentOut'];
export type UploadResult = Schemas['UploadResultOut'];
export type AnswerOut = Schemas['AnswerOut'];
export type CitationOut = Schemas['CitationOut'];
export type MessageOut = Schemas['MessageOut'];
export type PageOut = Schemas['PageOut'];
export type GrantOut = Schemas['GrantOut'];
export type AuditPage = Schemas['AuditPage'];
export type UsageReport = Schemas['UsageReport'];
export type Role = 'bd' | 'manager' | 'security_admin';

export const API_BASE = '/api/v1';

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/** Lỗi mạng (mất kết nối, máy chủ không phản hồi) — khác lỗi do máy chủ trả về. */
export class NetworkError extends Error {
  constructor() {
    super('Mất kết nối');
    this.name = 'NetworkError';
  }
}

type UnauthorizedHandler = (code: string) => void;
let onUnauthorized: UnauthorizedHandler | null = null;

export function setUnauthorizedHandler(handler: UnauthorizedHandler | null): void {
  onUnauthorized = handler;
}

const GENERIC_MESSAGE = 'Đã có lỗi xảy ra. Hãy thử lại sau.';

export async function toApiError(response: Response): Promise<ApiError> {
  let code = 'error';
  let message = GENERIC_MESSAGE;
  try {
    const body = (await response.json()) as { error?: { code?: string; message?: string } };
    code = body.error?.code ?? code;
    message = body.error?.message ?? message;
  } catch {
    // thân phản hồi không phải JSON (ví dụ proxy lỗi): dùng thông điệp chung
  }
  return new ApiError(response.status, code, message);
}

export function notifyUnauthorized(error: ApiError, path: string): void {
  // Sai mật khẩu ở chính màn hình đăng nhập không phải "hết phiên"
  if (error.status === 401 && !path.startsWith('/auth/login')) onUnauthorized?.(error.code);
}

export interface RequestOptions {
  method?: string;
  body?: unknown;
  signal?: AbortSignal;
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const init: RequestInit = {
    method: options.method ?? 'GET',
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
    signal: options.signal,
  };
  if (options.body !== undefined) {
    init.body = JSON.stringify(options.body);
    init.headers = { ...init.headers, 'Content-Type': 'application/json' };
  }
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, init);
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') throw err;
    throw new NetworkError();
  }
  if (!response.ok) {
    const error = await toApiError(response);
    notifyUnauthorized(error, path);
    throw error;
  }
  if (response.status === 204 || response.status === 202) {
    const text = await response.text();
    return (text ? JSON.parse(text) : undefined) as T;
  }
  return (await response.json()) as T;
}

export const api = {
  me: () => apiFetch<Me>('/auth/me'),
  login: (login: string, password: string) =>
    apiFetch<Me>('/auth/login', { method: 'POST', body: { login, password } }),
  logout: () => apiFetch<void>('/auth/logout', { method: 'POST' }),

  listDocuments: () => apiFetch<DocumentOut[]>('/documents'),
  retryDocument: (id: string) => apiFetch<DocumentOut>(`/documents/${id}/retry`, { method: 'POST' }),
  deleteDocument: (id: string) =>
    apiFetch<{ id: string; status: string }>(`/documents/${id}`, { method: 'DELETE' }),
  page: (id: string, page: number) => apiFetch<PageOut>(`/documents/${id}/pages/${page}`),
  sourceOpened: (documentId: string, page: number) =>
    apiFetch<void>('/events/source-opened', {
      method: 'POST',
      body: { document_id: documentId, page },
    }),

  createConversation: () => apiFetch<{ id: string }>('/conversations', { method: 'POST' }),
  messages: (conversationId: string) =>
    apiFetch<MessageOut[]>(`/conversations/${conversationId}/messages`),
  ask: (conversationId: string, question: string, signal?: AbortSignal) =>
    apiFetch<AnswerOut>(`/conversations/${conversationId}/messages`, {
      method: 'POST',
      body: { question },
      signal,
    }),
  feedback: (messageId: string, value: 'helpful' | 'not_helpful') =>
    apiFetch<void>(`/messages/${messageId}/feedback`, { method: 'PUT', body: { value } }),

  listAccess: () => apiFetch<GrantOut[]>('/admin/access'),
  grantAccess: (login: string, role: Role) =>
    apiFetch<GrantOut>('/admin/access', { method: 'POST', body: { login, role } }),
  revokeAccess: (userId: string) =>
    apiFetch<void>(`/admin/access/${userId}`, { method: 'DELETE' }),
  audit: (query: URLSearchParams) => apiFetch<AuditPage>(`/admin/audit?${query.toString()}`),
  usage: (weeks: number) => apiFetch<UsageReport>(`/reports/usage?weeks=${weeks}`),
};
