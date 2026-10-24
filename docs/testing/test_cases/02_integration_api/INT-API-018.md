# INT-API-018 — Giới hạn số chunk mỗi tài liệu

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | `MAX_CHUNKS_PER_DOC` giới hạn số chunk của một tài liệu; kết quả xếp theo điểm giảm dần |
| Truy vết | BR-007, US-009, T2-02 |
| Ưu tiên / Loại | Trung bình / Dương |
| Tự động hóa | `test_retrieval.py::test_max_chunks_per_document`; `test_qa_flow.py::test_question_across_documents_cites_the_right_one` |

**Các bước**
1. Tài liệu A: 6 chunk giống câu hỏi; B: 2 chunk. Truy xuất với `top_k = 8`, `per_doc = 4`.
2. Với HĐ-3T và BG-2T sẵn sàng: hỏi "Giá gói tiêu chuẩn lưu kho là bao nhiêu triệu?".

**Kết quả mong đợi**
- Bước 1: A có 4, B có 2; điểm giảm dần.
- Bước 2: citation đầu là BG-2T trang 2.
