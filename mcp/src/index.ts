#!/usr/bin/env node
// MCP server "Chat với tài liệu" (stdio). stdout dành cho giao thức MCP — mọi log ghi ra stderr.
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { ApiClient } from './client.js';
import { loadConfig } from './config.js';
import { registerTools } from './tools.js';

async function main(): Promise<void> {
  const config = loadConfig();
  const api = new ApiClient(config);
  const server = new McpServer(
    { name: 'chat-with-docs', version: '0.1.0' },
    {
      instructions:
        'Công cụ cho hệ thống "Chat với tài liệu": hỏi đáp trên các PDF người dùng đã tải lên, câu trả lời luôn kèm nguồn (tên tệp, số trang). ' +
        'Khi trả lời người dùng về nội dung tài liệu, dùng tool ask và giữ nguyên nguồn; nếu ask báo không tìm thấy, nói rõ như vậy thay vì tự suy đoán. ' +
        'Chỉ gọi delete_document khi người dùng đã xác nhận rõ tài liệu cần xóa.',
    },
  );
  registerTools(server, api, { uploadWaitSeconds: config.uploadWaitSeconds });
  await server.connect(new StdioServerTransport());
  console.error(`[chat-with-docs-mcp] sẵn sàng — ${config.apiUrl} (tài khoản ${config.login})`);

  const shutdown = async () => {
    await api.logout().catch(() => undefined);
    process.exit(0);
  };
  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}

main().catch((e) => {
  console.error(`[chat-with-docs-mcp] không khởi động được: ${(e as Error).message}`);
  process.exit(1);
});
