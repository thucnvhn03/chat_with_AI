# 03 — Ca kiểm thử hệ thống / đầu-cuối (E2E-001..E2E-013)

Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md) mục 6.1.3. Môi trường: `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.e2e.yml up -d --build` (adapter AI và embedding giả lập, tài khoản mẫu), trình duyệt Chromium qua Playwright, cửa sổ 1440×900, `http://localhost:5173`. Mật khẩu mọi tài khoản mẫu: `e2e-mat-khau-123`. Thư mục: `e2e/tests/`.

Nguyên tắc dữ liệu: mỗi lần chạy dùng tên tệp và từ vựng sinh ngẫu nhiên (`unique()`), để không bị nhiễu bởi tài liệu của lần chạy trước. PDF kiểm thử sinh bởi `e2e/tests/pdf.ts`.

## Danh sách ca (13)

| Mã ca | Tên |
|---|---|
| [E2E-001](E2E-001.md) | Đăng nhập đúng và sai |
| [E2E-002](E2E-002.md) | Người bị thu hồi quyền không vào được |
| [E2E-003](E2E-003.md) | Hết phiên giữ câu hỏi đang soạn |
| [E2E-004](E2E-004.md) | Trạng thái trống |
| [E2E-005](E2E-005.md) | Tải PDF hợp lệ tới "Sẵn sàng" |
| [E2E-006](E2E-006.md) | Tệp hỏng và tệp không phải PDF |
| [E2E-007](E2E-007.md) | Mất mạng khi tải lên |
| [E2E-008](E2E-008.md) | Hỏi đáp có nguồn và trình xem nguồn |
| [E2E-009](E2E-009.md) | Mất mạng khi hỏi |
| [E2E-010](E2E-010.md) | Xóa tài liệu |
| [E2E-011](E2E-011.md) | Quản trị quyền và bản ghi kiểm toán |
| [E2E-012](E2E-012.md) | Khả năng tiếp cận trên mọi màn hình |
| [E2E-013](E2E-013.md) | Ảnh màn hình đối chiếu với thiết kế |
