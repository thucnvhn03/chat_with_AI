# INT-API-010 — Lý do lỗi do worker xác định

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | PDF mã hóa, hỏng, chỉ ảnh qua được kiểm tra tải lên nhưng worker đánh dấu `failed` với đúng lý do và không tạo chunk |
| Truy vết | BR-003, BR-018, AC-003, AC-018, US-003, US-004, T1-15 |
| Ưu tiên / Loại | Cao / Âm |
| Dữ liệu | `mat-khau.pdf` (mã hóa), `hong.pdf` (hỏng), `scan.pdf` (chỉ ảnh) |
| Tự động hóa | `test_ingestion_flow.py::test_worker_failure_reasons` (3 trường hợp) |

**Các bước**
1. Tải từng tệp; chạy worker; `GET /documents/{id}`.

**Kết quả mong đợi**
- (`failed`, `encrypted`), (`failed`, `corrupted`), (`failed`, `no_text`); số chunk = 0.
