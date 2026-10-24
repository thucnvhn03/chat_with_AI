# Đặc tả ca kiểm thử — "Chat với tài liệu" (MVP)

Chi tiết hóa các ca kiểm thử của [Master_Test_Plan.md](../Master_Test_Plan.md) theo IEEE 829-2008 (Test Case Specification). Mỗi thư mục tương ứng một nhóm ca trong mục 6.1 của kế hoạch; mỗi ca kiểm thử là một tệp riêng `<Mã ca>.md`, `README.md` của thư mục chứa phần chung và danh sách ca của nhóm.

| Thư mục | Nhóm | Mã ca | Số ca | Mục kế hoạch |
|---|---|---|---|---|
| [01_unit/](01_unit/README.md) | Kiểm thử đơn vị | UT-001..UT-022 | 22 | 6.1.1 |
| [02_integration_api/](02_integration_api/README.md) | Kiểm thử tích hợp API | INT-API-001..INT-API-040 | 40 | 6.1.2 |
| [03_e2e_system/](03_e2e_system/README.md) | Kiểm thử hệ thống (đầu-cuối) | E2E-001..E2E-013 | 13 | 6.1.3 |
| [04_acceptance/](04_acceptance/README.md) | Kiểm thử chấp nhận | UAT-001..UAT-011 | 11 | 6.1.4 |
| [05_performance/](05_performance/README.md) | Kiểm thử hiệu năng | PERF-001..PERF-006 | 6 | 6.1.6 |
| [06_security/](06_security/README.md) | Kiểm thử bảo mật | SEC-001..SEC-013 | 13 | 6.1.7 |
| [07_accessibility/](07_accessibility/README.md) | Kiểm thử khả năng tiếp cận | ACC-001..ACC-008 | 8 | 6.1.8 |
| [08_ui/](08_ui/README.md) | Kiểm thử giao diện | UI-001..UI-008 | 8 | 6.1.9 |
| [09_api/](09_api/README.md) | Kiểm thử API (hợp đồng) | API-001..API-015 | 15 | 6.1.10 |
| [10_quality_evaluation/](10_quality_evaluation/README.md) | Kiểm thử chất lượng câu trả lời | QE-001..QE-008 | 8 | 6.1.11 |
| [11_operations/](11_operations/README.md) | Kiểm thử vận hành và sẵn sàng | OPS-001..OPS-005 | 5 | 6.1.12 |

## Mẫu đặc tả

Mỗi ca kiểm thử có các mục sau.

| Mục | Ý nghĩa |
|---|---|
| Mục tiêu | Điều ca kiểm thử chứng minh |
| Truy vết | BR / AC / US / task / tiêu chí launch liên quan |
| Ưu tiên | Cao / Trung bình / Thấp (theo ma trận rủi ro, kế hoạch mục 4.1) |
| Loại | Dương, âm, biên, lỗi, đồng thời, bảo mật… |
| Môi trường | Theo kế hoạch mục 11.1 |
| Điều kiện trước | Trạng thái hệ thống trước khi chạy |
| Dữ liệu | Dữ liệu đầu vào cụ thể |
| Các bước | Thao tác đánh số, lặp lại được |
| Kết quả mong đợi | Điều kiện đạt, đo được |
| Tự động hóa | Tệp và tên hàm kiểm thử hiện có, hoặc "Thủ công" |

## Quy ước chung

- **Đường dẫn API** đều có tiền tố `/api/v1` (trừ `/health/*`, `/metrics`). Yêu cầu thay đổi dữ liệu luôn kèm header `Origin: http://localhost:5173` (trừ ca kiểm thử CSRF).
- **Ngưỡng** lấy từ cấu hình (`backend/app/config.py`, `deploy/env.example`); khi chưa chốt dùng giá trị mặc định tạm: `MAX_FILE_BYTES` 20 MB, `MAX_DOCS_PER_USER` 50, `MAX_QUESTION_CHARS` 2000, `SESSION_IDLE_HOURS` 8, `LOGIN_MAX_FAILURES` 5 / 15 phút, `JOB_MAX_ATTEMPTS` 3, `TOP_K` 8, `MAX_CHUNKS_PER_DOC` 4, `ANSWER_TIMEOUT_S` 60, `HISTORY_TURNS` 4, `PURGE_SLA_HOURS` 24, `AUDIT_RETENTION_DAYS` 365, `MESSAGE_RETENTION_DAYS` 60. Kiểm thử tự động có thể đặt giá trị khác qua cấu hình.
- **Tài khoản mẫu E2E** (tạo bởi dịch vụ `seed` trong `deploy/docker-compose.e2e.yml`, mật khẩu `e2e-mat-khau-123`): `e2e.bd`, `e2e.bd2`, `e2e.empty` (BD chưa có tài liệu), `e2e.revoke` (BD dùng để thử thu hồi), `e2e.admin` (quản trị bảo mật), `e2e.manager` (quản lý).
- **Kiểm thử tích hợp** chạy trên PostgreSQL + pgvector và kho S3 thật, adapter AI giả lập (`FakeAnswerGenerator`), embedding giả lập (`HashEmbeddingProvider`), ngưỡng truy xuất 0,2. Mỗi kiểm thử bắt đầu với cơ sở dữ liệu trống.
- **Chạy kiểm thử tự động:** backend `scripts/backend-docker.sh`; frontend `cd frontend && npm test`; E2E `cd e2e && npx playwright test`; bộ đánh giá `cd evaluation && pytest`.
- **Kết quả** mỗi lần chạy ghi vào công cụ quản lý kiểm thử hoặc báo cáo tổng kết (kế hoạch mục 9), gồm: ngày, phiên bản mã, môi trường, Đạt/Không đạt, mã lỗi liên quan.
