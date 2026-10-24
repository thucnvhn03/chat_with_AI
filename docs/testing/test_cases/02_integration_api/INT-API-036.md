# INT-API-036 — Health báo lỗi khi thành phần dừng

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | `/health/ready` báo đúng thành phần lỗi: kho tệp, cơ sở dữ liệu, hàng đợi tồn đọng |
| Truy vết | BR-022, AC-022, US-021, T4-04 |
| Ưu tiên / Loại | Trung bình / Lỗi |
| Tự động hóa | `test_admin_reports_health.py::test_ready_ok_when_everything_is_up`, `test_ready_fails_when_storage_is_down`, `test_ready_fails_when_database_is_down`, `test_ready_fails_when_queue_backlog_is_old` |

**Các bước**
1. `GET /health/ready` khi mọi thứ chạy.
2. Thay kho tệp bằng bản ném lỗi; gọi lại.
3. Trỏ cơ sở dữ liệu tới địa chỉ không tồn tại; gọi lại.
4. Thêm việc có `run_after` lùi 2 giờ; gọi lại.

**Kết quả mong đợi**
- 200 với thành phần `database`, `storage`, `queue`.
- 503, `storage.ok = false`, `database.ok = true`.
- 503, `database.ok = false`.
- 503, `queue = {"ok": false, "detail": "queue_backlog"}`.
