# INT-API-022 — Dịch vụ AI từ chối hoặc quá thời gian

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Mô hình từ chối → 502 thông báo chung; quá `ANSWER_TIMEOUT_S` → 504 đúng hạn |
| Truy vết | BR-011, US-013, T2-05, T3-06 |
| Ưu tiên / Loại | Cao / Lỗi |
| Tự động hóa | `test_qa_flow.py::test_model_refusal_returns_generic_error`, `test_timeout_returns_504`, `test_slow_generator_hits_answer_timeout` |

**Các bước**
1. Adapter chế độ `refuse`: gửi câu hỏi.
2. Adapter chế độ `timeout`: gửi câu hỏi.
3. `ANSWER_TIMEOUT_S = 0,5`, adapter chờ 1,5 s: gửi câu hỏi, đo thời gian.

**Kết quả mong đợi**
- Bước 1: 502 `answer_unavailable`.
- Bước 2: 504 `answer_timeout`.
- Bước 3: 504 trong < 1,4 s.
