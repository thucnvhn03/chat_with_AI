// Kiểm thử tích hợp: chạy MCP server (dist/index.js) như tiến trình stdio thật, gọi backend thật của stack E2E
// (deploy/docker-compose.yml + docker-compose.e2e.yml: AI giả lập, embedding hash, tài khoản e2e.*).
// Bỏ qua trừ khi đặt CWD_IT=1. Cần `npm run build` trước.
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { makePdf } from '../../../e2e/tests/pdf';

const enabled = process.env.CWD_IT === '1';
const PASSWORD = process.env.CWD_IT_PASSWORD ?? 'e2e-mat-khau-123';
const API = process.env.CWD_API_URL ?? 'http://localhost:8000/api/v1';

async function connect(login: string): Promise<{ client: Client; call: (n: string, a?: Record<string, unknown>) => Promise<{ text: string; isError: boolean }> }> {
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [fileURLToPath(new URL('../../dist/index.js', import.meta.url))],
    env: { ...process.env, CWD_LOGIN: login, CWD_PASSWORD: PASSWORD, CWD_API_URL: API } as Record<string, string>,
    stderr: 'pipe',
  });
  const client = new Client({ name: 'it', version: '0' });
  await client.connect(transport);
  const call = async (name: string, args: Record<string, unknown> = {}) => {
    const r = await client.callTool({ name, arguments: args }, undefined, { timeout: 240_000 });
    return { text: (r.content as { text: string }[]).map((c) => c.text).join('\n'), isError: Boolean(r.isError) };
  };
  return { client, call };
}

describe.skipIf(!enabled)('MCP ↔ backend thật (stack E2E)', () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'cwd-mcp-'));
  const code = `MCP${Date.now().toString(36).toUpperCase()}`;
  const name = `HopDong_${code}.pdf`;
  let bd: Awaited<ReturnType<typeof connect>>;
  let docId = '';

  beforeAll(async () => {
    writeFileSync(path.join(dir, name), makePdf([
      'Hop dong dich vu giua Cong ty Alpha va Cong ty Beta nam 2026.',
      `Dieu 4. Ma du an cua hop dong la ${code} va duoc bao mat.`,
      'Dieu 5. Thoi han thanh toan la 30 ngay ke tu ngay nghiem thu.',
    ]));
    writeFileSync(path.join(dir, 'ghichu.txt'), 'khong phai pdf');
    bd = await connect('e2e.bd');
  }, 60_000);

  afterAll(async () => {
    await bd?.client.close();
    rmSync(dir, { recursive: true, force: true });
  });

  it('whoami: vai trò BD và giới hạn từ cấu hình', async () => {
    const r = await bd.call('whoami');
    expect(r.isError).toBe(false);
    expect(r.text).toContain('Vai trò: Nhân sự BD');
    expect(r.text).toMatch(/tệp tối đa [\d.]+ MB/);
  });

  it('upload_documents: PDF hợp lệ tới Sẵn sàng, tệp .txt bị từ chối sớm', async () => {
    const r = await bd.call('upload_documents', { paths: [path.join(dir, name), path.join(dir, 'ghichu.txt')] });
    expect(r.text).toContain('✗ ghichu.txt: Tệp không phải PDF');
    expect(r.text).toMatch(new RegExp(`✓ ${name}: Sẵn sàng, 3 trang \\(id ([0-9a-f-]{36})\\)`));
    docId = r.text.match(new RegExp(`${name}: Sẵn sàng, 3 trang \\(id ([0-9a-f-]{36})\\)`))![1];
  }, 240_000);

  it('list_documents: tài liệu vừa tải có trong danh sách', async () => {
    const r = await bd.call('list_documents', { status: 'ready' });
    expect(r.text).toContain(`${name} · Sẵn sàng · 3 trang`);
  });

  it('ask: câu trả lời chứa nội dung và nguồn đúng tệp, đúng trang', async () => {
    const r = await bd.call('ask', { question: `Ma du an ${code} cua hop dong la gi?`, new_conversation: true });
    expect(r.isError).toBe(false);
    expect(r.text).toContain(code);
    expect(r.text).toContain(`${name}, tr. 2`);
    expect(r.text).toContain(`document_id ${docId}`);
  }, 120_000);

  it('get_source_page: đọc đúng trang được trích', async () => {
    const r = await bd.call('get_source_page', { document_id: docId, page: 2 });
    expect(r.text).toContain(`${name} — trang 2/3`);
    expect(r.text).toContain(code);
  });

  it('ask: câu hỏi ngoài phạm vi → không tìm thấy, không bịa', async () => {
    const r = await bd.call('ask', { question: 'Capital city of Australia?', new_conversation: true });
    expect(r.text).toContain('KHÔNG TÌM THẤY');
    expect(r.text).not.toContain('Nguồn:');
  }, 120_000);

  it('cô lập: tài khoản BD khác không đọc được tài liệu này', async () => {
    const other = await connect('e2e.bd2');
    try {
      const r = await other.call('get_source_page', { document_id: docId, page: 2 });
      expect(r.isError).toBe(true);
      expect(r.text).not.toContain(code);
    } finally {
      await other.client.close();
    }
  });

  it('usage_report: BD bị từ chối, quản lý xem được', async () => {
    const denied = await bd.call('usage_report', { weeks: 4 });
    expect(denied.isError).toBe(true);
    expect(denied.text).toContain('[forbidden_role]');
    const manager = await connect('e2e.manager');
    try {
      const r = await manager.call('usage_report', { weeks: 4 });
      expect(r.isError).toBe(false);
      expect(r.text).toContain('| Tuần (từ thứ Hai) |');
    } finally {
      await manager.client.close();
    }
  });

  it('delete_document: xóa tài liệu kiểm thử (dọn dẹp)', async () => {
    const r = await bd.call('delete_document', { document_id: docId, confirm_file_name: name });
    expect(r.isError).toBe(false);
    expect(r.text).toContain(`Đã xóa "${name}"`);
  });
});
