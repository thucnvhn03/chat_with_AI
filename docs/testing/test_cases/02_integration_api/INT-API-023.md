# INT-API-023 — Mỗi câu hỏi đúng một bản ghi kiểm toán, không nội dung

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Mỗi câu hỏi (kể cả "không tìm thấy") sinh đúng một `audit_records` liệt kê tài liệu được phép, một `question_submitted`, một `answer_returned`; không có nội dung câu hỏi |
| Truy vết | BR-023, AC-023, US-020, T2-05 |
| Ưu tiên / Loại | Cao / Dương |
| Tự động hóa | `test_qa_flow.py::test_each_question_writes_exactly_one_audit_record_without_content`; `test_migrations.py::test_audit_and_usage_tables_have_no_content_columns` |

**Các bước**
1. Hỏi 2 câu (một trong phạm vi, một ngoài phạm vi).
2. Đọc `audit_records`, `usage_events`; đọc danh sách cột hai bảng.

**Kết quả mong đợi**
- 2 bản ghi kiểm toán; `document_ids` = {HĐ-3T, BG-2T}.
- 2 `question_submitted`, 2 `answer_returned`.
- Hai bảng không có cột `question`, `content`, `text`, `answer`, `body`.
