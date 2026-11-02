// Bản sao tạm của cấu hình E2E có chụp ảnh mọi ca (run_layers.sh chép vào e2e/ rồi xóa sau khi chạy).
// Cấu hình gốc chỉ chụp khi lỗi; ở đây chụp mọi ca để làm bằng chứng và xuất JSON để biết ảnh thuộc ca nào.
import { defineConfig } from '@playwright/test';
import base from './playwright.config';

const OUT = process.env.EVIDENCE_DIR ?? '../test-results/run-evidence';

export default defineConfig({
  ...base,
  outputDir: `${OUT}/pw-output`,
  reporter: [
    ['list'],
    ['junit', { outputFile: `${OUT}/e2e-playwright.xml` }],
    ['json', { outputFile: `${OUT}/e2e-playwright.json` }],
    ['html', { open: 'never' }],
  ],
  use: { ...base.use, screenshot: 'on' },
});
