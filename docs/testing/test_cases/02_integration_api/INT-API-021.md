# INT-API-021 — Kiểm tra độ dài câu hỏi

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Câu hỏi rỗng hoặc dài hơn `MAX_QUESTION_CHARS` bị từ chối |
| Truy vết | US-008, PRD 4.2, T2-05 |
| Ưu tiên / Loại | Trung bình / Biên |
| Tự động hóa | `test_qa_flow.py::test_question_validation` |

**Các bước**
1. Gửi câu hỏi "   ".
2. Gửi câu hỏi 2001 ký tự.

**Kết quả mong đợi**
- 400 `question_empty`; 400 `question_too_long`.
