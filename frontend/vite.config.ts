/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// Trong Docker Compose, VITE_API_PROXY_TARGET trỏ tới dịch vụ backend (xem deploy/docker-compose.yml).
const apiTarget = process.env.VITE_API_PROXY_TARGET ?? 'http://localhost:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { '/api': { target: apiTarget, changeOrigin: true } },
    // Thư mục gắn vào container trên Windows/macOS không phát sự kiện tệp; thăm dò khi được bật
    watch: { usePolling: process.env.CHOKIDAR_USEPOLLING === 'true' },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/setupTests.ts'],
    // jsdom + axe chậm trên máy CI/máy phát triển đang tải nặng
    testTimeout: 20_000,
  },
});
