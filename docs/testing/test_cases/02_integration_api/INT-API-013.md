# INT-API-013 — Nhiều worker không lấy trùng việc

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | `FOR UPDATE SKIP LOCKED` bảo đảm không việc nào bị xử lý hai lần; nhiều tệp được nạp song song đúng |
| Truy vết | ADR-003, T1-12, AC-002 |
| Ưu tiên / Loại | Cao / Đồng thời |
| Tự động hóa | `test_storage_and_queue.py::test_two_workers_never_claim_the_same_job`; `test_ingestion_flow.py::test_many_files_with_two_concurrent_workers` |

**Các bước**
1. Thêm 40 việc; chạy 4 worker song song.
2. Tải 10 PDF hợp lệ + 1 PDF hỏng; chạy 2 worker song song.

**Kết quả mong đợi**
- Bước 1: tập việc đã xử lý = {0..39}, không trùng; mọi việc `done`.
- Bước 2: 10 tài liệu `ready`, tệp hỏng `failed`.
