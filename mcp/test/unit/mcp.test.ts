// Kiểm thử MCP server qua giao thức thật (Client ↔ InMemoryTransport ↔ McpServer) với backend giả lập.
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { InMemoryTransport } from '@modelcontextprotocol/sdk/inMemory.js';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { describe, expect, it } from 'vitest';
import { ApiClient } from '../../src/client.js';
import { loadConfig } from '../../src/config.js';
import { registerTools, type ToolDeps } from '../../src/tools.js';
import { fakeBackend, IDS } from './fakeBackend.js';

const PDF = new TextEncoder().encode('%PDF-1.4\n%fake\n');

async function setup(opts: { role?: string; password?: string; files?: Record<string, Uint8Array>; processingPolls?: number } = {}) {
  const backend = fakeBackend({ role: opts.role, processingPolls: opts.processingPolls });
  const config = loadConfig({ CWD_LOGIN: 'e2e.bd', CWD_PASSWORD: opts.password ?? 'dung', CWD_API_URL: 'http://api.test/api/v1/' });
  const api = new ApiClient(config, backend.fetch);
  const files = opts.files ?? {};
  const deps: Partial<ToolDeps> = {
    readFile: async (p) => files[p.replace(/\\/g, '/').split('/').pop()!] ?? Promise.reject(new Error('ENOENT')),
    fileSize: async (p) => {
      const f = files[p.replace(/\\/g, '/').split('/').pop()!];
      if (!f) throw new Error('ENOENT');
      return f.length;
    },
    sleep: async () => undefined,
    uploadWaitSeconds: 60,
  };
  const server = new McpServer({ name: 'test', version: '0' });
  registerTools(server, api, deps);
  const [a, b] = InMemoryTransport.createLinkedPair();
  const client = new Client({ name: 'test-client', version: '0' });
  await Promise.all([server.connect(a), client.connect(b)]);
  const call = async (name: string, args: Record<string, unknown> = {}) => {
    const r = await client.callTool({ name, arguments: args });
    return { text: (r.content as { text: string }[]).map((c) => c.text).join('\n'), isError: Boolean(r.isError) };
  };
  return { backend, client, call };
}

describe('danh mục tool', () => {
  it('đủ 11 tool, chú thích đọc/ghi/xóa đúng', async () => {
    const { client } = await setup();
    const { tools } = await client.listTools();
    const byName = Object.fromEntries(tools.map((t) => [t.name, t]));
    expect(Object.keys(byName).sort()).toEqual([
      'ask', 'delete_document', 'get_conversation', 'get_source_page', 'list_documents', 'new_conversation',
      'retry_document', 'send_feedback', 'upload_documents', 'usage_report', 'whoami',
    ]);
    expect(byName.delete_document.annotations?.destructiveHint).toBe(true);
    expect(byName.list_documents.annotations?.readOnlyHint).toBe(true);
    expect(byName.ask.inputSchema.required).toEqual(['question']);
  });
});

describe('phiên và bảo mật', () => {
  it('đăng nhập một lần, GET không gửi Origin, yêu cầu thay đổi dữ liệu gửi Origin và cookie phiên', async () => {
    const { backend, call } = await setup();
    await call('list_documents');
    await call('ask', { question: 'Thời hạn thanh toán?' });
    expect(backend.calls.filter((c) => c.path === '/auth/login')).toHaveLength(1);
    const list = backend.calls.find((c) => c.path === '/documents' && c.method === 'GET')!;
    expect(list.headers.origin).toBeUndefined();
    expect(list.headers.cookie).toBe('cwd_session=t1');
    const ask = backend.calls.find((c) => c.path.endsWith('/messages') && c.method === 'POST')!;
    expect(ask.headers.origin).toBe('http://localhost:5173');
    expect(ask.headers.cookie).toBe('cwd_session=t1');
  });

  it('phiên hết hạn: đăng nhập lại một lần rồi gửi lại yêu cầu', async () => {
    const { backend, call } = await setup();
    await call('list_documents');
    backend.state.expireNext = true;
    const r = await call('list_documents');
    expect(r.isError).toBe(false);
    expect(backend.calls.filter((c) => c.path === '/auth/login')).toHaveLength(2);
  });

  it('sai mật khẩu: lỗi đọc được kèm gợi ý cấu hình, không lộ mật khẩu', async () => {
    const { call } = await setup({ password: 'sai-mat-khau' });
    const r = await call('whoami');
    expect(r.isError).toBe(true);
    expect(r.text).toContain('[invalid_credentials]');
    expect(r.text).toContain('CWD_PASSWORD');
    expect(r.text).not.toContain('sai-mat-khau');
  });

  it('sai vai trò: backend từ chối, tool trả lỗi forbidden_role', async () => {
    const { call } = await setup({ role: 'manager' });
    const r = await call('list_documents');
    expect(r.isError).toBe(true);
    expect(r.text).toContain('[forbidden_role]');
  });
});

describe('tài liệu', () => {
  it('danh sách có trạng thái, số trang và lý do lỗi bằng tiếng Việt', async () => {
    const { call } = await setup();
    const r = await call('list_documents');
    expect(r.text).toContain('2 tài liệu (1 sẵn sàng)');
    expect(r.text).toContain(`HopDong_A.pdf · Sẵn sàng · 3 trang · 117 KB (id ${IDS.DOC_A})`);
    expect(r.text).toContain('Hong.pdf · Lỗi');
    expect(r.text).toContain('Tệp bị hỏng hoặc không đọc được');
    expect(r.text).not.toContain('corrupted');
  });

  it('tải lên: từ chối sớm tệp không phải PDF, chờ tệp hợp lệ tới Sẵn sàng', async () => {
    const { backend, call } = await setup({ files: { 'BaoGia.pdf': PDF, 'ghichu.txt': new Uint8Array([1]), 'gia.pdf': new TextEncoder().encode('xin chao') } });
    const r = await call('upload_documents', { paths: ['/tmp/BaoGia.pdf', '/tmp/ghichu.txt', '/tmp/gia.pdf'] });
    expect(r.text).toContain('✗ ghichu.txt: Tệp không phải PDF');
    expect(r.text).toContain('✗ gia.pdf: Tệp không phải PDF'); // đuôi .pdf nhưng nội dung không phải PDF
    expect(r.text).toMatch(/✓ BaoGia\.pdf: Sẵn sàng, 2 trang/);
    const upload = backend.calls.find((c) => c.path === '/documents' && c.method === 'POST')!;
    expect((upload.body as FormData).getAll('files')).toHaveLength(1);
    expect(upload.headers.origin).toBe('http://localhost:5173');
  });

  it('tải lên: tệp không tồn tại → lỗi, không gọi backend', async () => {
    const { backend, call } = await setup();
    const r = await call('upload_documents', { paths: ['/tmp/khong-co.pdf'] });
    expect(r.isError).toBe(true);
    expect(r.text).toContain('không tìm thấy tệp');
    expect(backend.calls.some((c) => c.path === '/documents' && c.method === 'POST')).toBe(false);
  });

  it('xóa: tên xác nhận không khớp thì không xóa', async () => {
    const { backend, call } = await setup();
    const r = await call('delete_document', { document_id: IDS.DOC_A, confirm_file_name: 'HopDong_B.pdf' });
    expect(r.isError).toBe(true);
    expect(backend.calls.some((c) => c.method === 'DELETE')).toBe(false);
  });

  it('xóa: tên khớp thì xóa và báo thời hạn xóa vĩnh viễn', async () => {
    const { backend, call } = await setup();
    const r = await call('delete_document', { document_id: IDS.DOC_A, confirm_file_name: 'HopDong_A.pdf' });
    expect(r.isError).toBe(false);
    expect(r.text).toContain('xóa vĩnh viễn trong 24 giờ');
    expect(backend.calls.filter((c) => c.method === 'DELETE')).toHaveLength(1);
  });
});

describe('hỏi đáp', () => {
  it('trả lời kèm nguồn (tên tệp, số trang, document_id) và dùng chung một hội thoại cho câu hỏi tiếp', async () => {
    const { backend, call } = await setup();
    const r1 = await call('ask', { question: 'Thời hạn thanh toán?' });
    expect(r1.text).toContain('Thời hạn thanh toán là 30 ngày.');
    expect(r1.text).toContain(`[1] HopDong_A.pdf, tr. 2 — "thanh toan trong 30 ngay" (document_id ${IDS.DOC_A})`);
    await call('ask', { question: 'Còn hợp đồng B thì sao?' });
    expect(backend.state.conversations).toHaveLength(1);
    const asks = backend.calls.filter((c) => c.path.endsWith('/messages') && c.method === 'POST');
    expect(new Set(asks.map((c) => c.path)).size).toBe(1);
  });

  it('new_conversation / new_conversation=true tạo hội thoại mới', async () => {
    const { backend, call } = await setup();
    await call('ask', { question: 'Câu 1' });
    await call('new_conversation');
    await call('ask', { question: 'Câu 2', new_conversation: true });
    expect(backend.state.conversations).toHaveLength(3);
  });

  it('không tìm thấy: nói rõ, không có nguồn', async () => {
    const { call } = await setup();
    const r = await call('ask', { question: 'Thu do cua Uc?' });
    expect(r.text).toContain('KHÔNG TÌM THẤY thông tin này trong các tài liệu đã tải lên.');
    expect(r.text).not.toContain('Nguồn:');
  });

  it('đọc trang nguồn và ghi sự kiện mở nguồn', async () => {
    const { backend, call } = await setup();
    const r = await call('get_source_page', { document_id: IDS.DOC_A, page: 2 });
    expect(r.text).toContain('HopDong_A.pdf — trang 2/3');
    expect(backend.state.events).toEqual([{ document_id: IDS.DOC_A, page: 2 }]);
    const missing = await call('get_source_page', { document_id: IDS.DOC_A, page: 9 });
    expect(missing.isError).toBe(true);
    expect(missing.text).toContain('Trang không tồn tại');
  });

  it('lịch sử hội thoại và đánh giá', async () => {
    const { backend, call } = await setup();
    expect((await call('get_conversation')).text).toContain('Chưa có hội thoại');
    const r = await call('ask', { question: 'Thời hạn thanh toán?' });
    const messageId = r.text.match(/message_id ([0-9a-f-]{36})/)![1];
    expect((await call('get_conversation')).text).toContain('Đáp: Thời hạn thanh toán là 30 ngày.');
    await call('send_feedback', { message_id: messageId, value: 'helpful' });
    expect(backend.state.feedback.get(messageId)).toBe('helpful');
  });

  it('tham số sai bị chặn trước khi gọi backend', async () => {
    const { backend, call } = await setup();
    const r = await call('get_source_page', { document_id: 'khong-phai-uuid', page: 0 });
    expect(r.isError).toBe(true);
    expect(backend.calls.some((c) => c.path.includes('/pages/'))).toBe(false);
  });
});

describe('báo cáo', () => {
  it('quản lý xem được báo cáo sử dụng theo tuần', async () => {
    const { call } = await setup({ role: 'manager' });
    const r = await call('usage_report', { weeks: 4 });
    expect(r.text).toContain('| 2026-10-26 | 7 | 42 | 80% | 10 |');
  });
});
