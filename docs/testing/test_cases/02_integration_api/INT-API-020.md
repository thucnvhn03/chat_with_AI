# INT-API-020 — Câu ngoài phạm vi không gọi mô hình

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Câu không liên quan nhận "không tìm thấy" mà không gọi dịch vụ AI (không gửi dữ liệu ra ngoài) |
| Truy vết | BR-009, AC-009, US-011, T2-12 |
| Ưu tiên / Loại | Cao / Âm |
| Tự động hóa | `test_qa_flow.py::test_out_of_scope_question_is_not_found_without_calling_model`, `test_model_answers_without_valid_citation_become_not_found` |

**Các bước**
1. Hỏi "Thủ đô của nước Úc là thành phố nào?".
2. Với adapter ở chế độ `no_citations`, `not_found_sentence`, `bad_index`: hỏi "Thời hạn thanh toán là bao nhiêu ngày?".

**Kết quả mong đợi**
- Bước 1: `not_found = true`, không citation, `answer` = câu từ chối cố định; số lời gọi adapter = 0.
- Bước 2: `not_found = true` ở cả 3 chế độ; số lời gọi adapter = 1.
