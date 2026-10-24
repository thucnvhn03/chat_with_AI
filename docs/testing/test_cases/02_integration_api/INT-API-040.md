# INT-API-040 — Dọn dữ liệu định kỳ theo thời hạn lưu

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Worker xóa bản ghi kiểm toán quá `AUDIT_RETENTION_DAYS` và hội thoại không hoạt động quá `MESSAGE_RETENTION_DAYS` (kèm tin nhắn, trích dẫn, đánh giá); dữ liệu mới giữ nguyên; giá trị 0 tắt việc dọn hội thoại |
| Truy vết | BR-023, PQ-004, OQ-012, T3-04 |
| Ưu tiên / Loại | Trung bình / Dương |
| Tự động hóa | `test_admin_reports_health.py::test_audit_retention_cleanup`; `test_qa_flow.py::test_inactive_conversations_are_cleaned_up`, `test_retention_zero_keeps_everything` |

**Các bước**
1. Tạo 1 bản ghi kiểm toán mới, 1 bản ghi 400 ngày trước; chạy dọn.
2. Hai hội thoại có câu trả lời (một được đánh giá); lùi hội thoại thứ nhất về quá `MESSAGE_RETENTION_DAYS` + 1 ngày; chạy việc định kỳ.
3. Gọi dọn hội thoại với giá trị 0.

**Kết quả mong đợi**
- Bước 1: xóa 1, còn 1.
- Bước 2: hội thoại cũ trả 404, hội thoại mới 200; 0 đánh giá; còn 1 citation; vẫn đủ 2 bản ghi kiểm toán.
- Bước 3: trả 0, không xóa gì.
- Ghi chú: hai kiểm thử của bước 2–3 đã viết nhưng **chưa được chạy** (tại ngày soạn).
