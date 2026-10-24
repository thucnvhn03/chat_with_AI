# PERF-003 — Thời gian nạp tài liệu

Nhóm: [05 — Ca kiểm thử hiệu năng (PERF-001..PERF-006)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Đo thời gian nạp và độ dài hàng đợi khi tải nhiều tệp |
| Truy vết | BR-002, AC-002, US-002 |
| Ưu tiên | Trung bình |
| Dữ liệu | 10 PDF (giới hạn tạm thời), gồm tệp lớn gần `MAX_FILE_BYTES` và tệp nhiều trang |
| Điều kiện trước | `WORKER_CONCURRENCY = 2` |

**Các bước**
1. Tải 10 tệp trong một yêu cầu.
2. Theo dõi `ingest_duration_seconds`, `jobs_queued{kind="ingest"}`, `jobs_oldest_queued_age_seconds` tới khi hết việc.

**Kết quả mong đợi**
- Mọi tệp `ready`.
- Không việc nào chờ quá `QUEUE_MAX_AGE_S` (600 s); `/health/ready` luôn 200.
- Ghi thời gian nạp theo số trang để ước lượng năng lực worker.
