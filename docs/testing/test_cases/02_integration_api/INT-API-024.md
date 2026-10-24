# INT-API-024 — Lỗi commit không bị nuốt

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Commit chạy trước khi gửi phản hồi; lỗi commit trả 500 chứ không 200 |
| Truy vết | TR-05 (lỗi hồi quy: API trả 200 dù không lưu được) |
| Ưu tiên / Loại | Cao / Hồi quy |
| Tự động hóa | `test_qa_flow.py::test_commit_failure_is_reported_not_swallowed` |

**Các bước**
1. Thay `Session.commit` bằng hàm ném lỗi.
2. `POST /conversations`.

**Kết quả mong đợi**
- 500.
