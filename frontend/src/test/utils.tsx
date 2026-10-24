// Tiện ích kiểm thử: dựng ứng dụng với router + TanStack Query, giả lập API bằng bảng xử lý theo
// "PHƯƠNG_THỨC /đường-dẫn", kiểm tra khả năng tiếp cận bằng axe-core.
import { QueryClientProvider } from '@tanstack/react-query';
import { render } from '@testing-library/react';
import axe from 'axe-core';
import type { ReactElement } from 'react';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';
import type { Me } from '../api/client';
import { AppRoutes, makeQueryClient } from '../app/App';

export type Handler = (body: unknown, url: URL) => unknown | Response | Promise<unknown | Response>;

export interface ApiMock {
  calls: { method: string; path: string; body: unknown }[];
  set: (key: string, handler: Handler) => void;
}

export function json(status: number, body: unknown): Response {
  return new Response(body === undefined ? null : JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

export function apiError(status: number, code: string, message = 'Lỗi'): Response {
  return json(status, { error: { code, message } });
}

/** Giả lập fetch: khóa là "GET /documents" (bỏ tiền tố /api/v1 và chuỗi truy vấn). */
export function mockApi(handlers: Record<string, Handler>): ApiMock {
  const table = new Map(Object.entries(handlers));
  const calls: ApiMock['calls'] = [];
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input), 'http://localhost');
      const method = (init?.method ?? 'GET').toUpperCase();
      const path = url.pathname.replace(/^\/api\/v1/, '');
      const body = init?.body ? JSON.parse(String(init.body)) : undefined;
      calls.push({ method, path, body });
      if (init?.signal?.aborted) throw new DOMException('Đã hủy', 'AbortError');
      const handler = table.get(`${method} ${path}`);
      if (!handler) return apiError(404, 'not_found', `Chưa giả lập ${method} ${path}`);
      const signal = init?.signal;
      // Như fetch thật: hủy yêu cầu làm promise bị từ chối ngay, kể cả khi máy chủ chưa trả lời
      const aborted = new Promise<never>((_, reject) =>
        signal?.addEventListener('abort', () => reject(new DOMException('Đã hủy', 'AbortError'))),
      );
      const result = await Promise.race([Promise.resolve(handler(body, url)), aborted]);
      if (result instanceof Response) return result;
      return json(result === undefined ? 204 : 200, result);
    }),
  );
  return { calls, set: (key, handler) => table.set(key, handler) };
}

export function makeMe(role: Me['role'] = 'bd', overrides: Partial<Me['config']> = {}): Me {
  return {
    user: { id: 'u-1', login: 'an.nguyen', display_name: 'Nguyễn An' },
    role,
    config: {
      max_file_bytes: 20 * 1024 * 1024,
      max_docs_per_user: 50,
      max_question_chars: 2000,
      poll_interval_s: 3,
      purge_sla_hours: 24,
      auth_mode: 'local',
      ...overrides,
    },
  };
}

export function renderApp(route: string, state?: unknown) {
  const queryClient = makeQueryClient();
  const result = render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[{ pathname: route.split('?')[0], search: route.includes('?') ? `?${route.split('?')[1]}` : '', state }]}>
        <AppRoutes />
      </MemoryRouter>
    </QueryClientProvider>,
  );
  return { ...result, queryClient };
}

export function renderWithProviders(ui: ReactElement) {
  const queryClient = makeQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>,
  );
}

/** Vi phạm axe mức nghiêm trọng hoặc cao (bỏ kiểm tra tương phản: jsdom không tính được màu). */
export async function seriousViolations(container: Element): Promise<string[]> {
  const results = await axe.run(container, {
    rules: { 'color-contrast': { enabled: false }, region: { enabled: false } },
  });
  return results.violations
    .filter((v) => v.impact === 'serious' || v.impact === 'critical')
    .map((v) => `${v.id}: ${v.help}`);
}
