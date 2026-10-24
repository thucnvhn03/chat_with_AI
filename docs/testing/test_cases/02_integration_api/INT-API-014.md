# INT-API-014 — Thử lại tài liệu lỗi

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Chỉ thử lại được tài liệu `failed`; thử lại đặt `processing` và thêm việc mới |
| Truy vết | BR-003, US-003, T1-16 |
| Ưu tiên / Loại | Trung bình / Dương, âm |
| Tự động hóa | `test_ingestion_flow.py::test_retry_only_for_failed_and_requeues` |

**Các bước**
1. Tải `hong.pdf` (hỏng) và `tot.pdf` (HĐ-3T); chạy worker.
2. `POST /documents/{tot}/retry`.
3. `POST /documents/{hong}/retry`; thay tệp trên kho bằng PDF hợp lệ; chạy worker.

**Kết quả mong đợi**
- Bước 2: 409 `not_retryable`.
- Bước 3: 200 `processing`; sau worker → `ready`.
