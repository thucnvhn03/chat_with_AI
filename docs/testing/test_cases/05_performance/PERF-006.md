# PERF-006 — Hết thời gian chờ đúng hạn

Nhóm: [05 — Ca kiểm thử hiệu năng (PERF-001..PERF-006)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Khi dịch vụ AI chậm, API trả 504 đúng hạn `ANSWER_TIMEOUT_S`, không treo kết nối |
| Truy vết | BR-011, US-013, T3-06 |
| Ưu tiên | Cao |
| Tự động hóa | `test_qa_flow.py::test_slow_generator_hits_answer_timeout` |

**Các bước**
1. Đặt `ANSWER_TIMEOUT_S = 0,5`; adapter giả lập chờ 1,5 s.
2. Gửi câu hỏi, đo thời gian.

**Kết quả mong đợi**
- 504 `answer_timeout` trong < 1,4 s (≤ `ANSWER_TIMEOUT_S` + 1 s).
- Giao diện hiển thị thông báo quá thời gian kèm "Thử lại" (Vitest `chat.test.tsx` — 504).
