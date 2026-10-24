# INT-API-019 — Câu trả lời có nguồn đúng tài liệu và trang

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Câu hỏi có đáp án nhận câu trả lời kèm citation đúng tài liệu và trang; đoạn trích có trong trang được nêu |
| Truy vết | BR-006, BR-012, BR-019, AC-006, AC-012, AC-019, T2-05, T2-12 |
| Ưu tiên / Loại | Cao / Dương |
| Điều kiện trước | HĐ-3T và BG-2T `ready` cho "an" |
| Tự động hóa | `test_qa_flow.py::test_answer_has_source_document_and_page` |

**Các bước**
1. `POST /conversations` → `id`.
2. `POST /conversations/{id}/messages` `{"question": "Thời hạn thanh toán là bao nhiêu ngày?"}`.
3. `GET /documents/{HĐ}/pages/{trang của citation}`.

**Kết quả mong đợi**
- `not_found = false`; `answer` chứa "30 ngày"; một citation (HĐ-3T, `HopDong_A.pdf`, trang 2); `latency_ms` ≥ 0.
- Văn bản trang 2 chứa `cited_text`; `page_count = 3`.
