# INT-API-011 — Lỗi tạm thời được thử lại rồi chuyển failed

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Lỗi đọc kho tệp được thử lại với giãn cách; hết `JOB_MAX_ATTEMPTS` thì việc `failed`, tài liệu `failed/internal`; lỗi chỉ một lần thì thành công |
| Truy vết | implement_plan 5.1 bước 8, T1-12, T1-15 |
| Ưu tiên / Loại | Cao / Lỗi |
| Tự động hóa | `test_ingestion_flow.py::test_transient_storage_error_retries_then_fails_internal`; `test_storage_and_queue.py::test_transient_error_is_retried_then_succeeds`, `test_job_fails_after_max_attempts_and_calls_give_up`, `test_backoff_delays_next_attempt` |

**Các bước**
1. Thay kho tệp bằng bản luôn ném `ConnectionError` khi đọc; tải PDF; chạy worker tới hết.
2. Với việc lỗi đúng một lần: chạy worker.
3. Với `JOB_RETRY_BASE_S = 3600`: chạy một việc lỗi rồi gọi lấy việc ngay.

**Kết quả mong đợi**
- Bước 1: tài liệu (`failed`, `internal`); việc `failed`, `attempts = JOB_MAX_ATTEMPTS`, `last_error` chứa tên lỗi.
- Bước 2: việc `done`, `attempts = 2`.
- Bước 3: lần lấy thứ hai không có việc; việc ở `queued` chờ tới lượt.
