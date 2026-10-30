# Kết quả kiểm thử — 2026-10-28

| Tầng | Công cụ | Kết quả | Thời gian | Tệp |
|---|---|---|---|---|
| Backend (unit, integration, security) | pytest | **185 đạt, 1 bỏ qua**, 0 lỗi | 13m56s | [backend-pytest.xml](backend-pytest.xml), [log](backend-pytest.log) |
| Frontend | Vitest | **79/79 đạt** (8 tệp) | 38s | [frontend-vitest.xml](frontend-vitest.xml), [log](frontend-vitest.log) |
| Đầu-cuối (giao diện thật, Chromium) | Playwright + axe | **20/20 đạt** | 2m36s | [e2e-playwright.xml](e2e-playwright.xml), [log](e2e-playwright.log) |

Ca bỏ qua: `tests/unit/test_claude_adapter.py:107` cần `ANTHROPIC_API_KEY` (gọi Claude thật).

## Môi trường

- Docker Compose `deploy/docker-compose.yml`; E2E thêm `deploy/docker-compose.e2e.yml` (AI giả lập `ANSWER_PROVIDER=fake`, embedding giả lập `hash`, tài khoản mẫu `e2e.*`).
- Backend chạy trong ảnh `cwd-backend-dev` qua `scripts/backend-docker.sh`, dùng PostgreSQL và kho S3 của compose.

## Ảnh chụp

- [screenshots/e2e/](screenshots/e2e/): ảnh trạng thái cuối của từng ca E2E, đặt tên `<số ca>_<tệp spec>_<tên ca>_<n>.png`.
  Ca mở thêm trang (09, 12) có nhiều ảnh, mỗi trang một ảnh.
- [screenshots/man-hinh/](screenshots/man-hinh/): ảnh các màn hình S-01..S-07 do `screenshots.spec.ts` chụp.
- Báo cáo HTML của Playwright (có ảnh đính kèm từng ca): `e2e/playwright-report/index.html`, mở bằng `cd e2e && npx playwright show-report`.

Ghi chú: `auth.spec.ts` (ca "không có quyền") và `delete-audit.spec.ts` (ca "quản trị bảo mật") mở trang bằng
`browser.newPage()` mà không đóng, nên khi bật `screenshot: 'on'` Playwright chụp lại các trang đó ở những ca sau.
Các ảnh trùng này đã được loại khỏi `screenshots/e2e/`.
