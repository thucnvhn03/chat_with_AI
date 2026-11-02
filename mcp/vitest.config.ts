import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // Kiểm thử tích hợp khởi động tiến trình MCP và đăng nhập backend thật (băm mật khẩu) ở mỗi kết nối
    testTimeout: 60_000,
    hookTimeout: 60_000,
  },
});
