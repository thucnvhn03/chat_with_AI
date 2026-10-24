# PERF-001 — Độ trễ hỏi đáp trên bộ câu hỏi chuẩn

Nhóm: [05 — Ca kiểm thử hiệu năng (PERF-001..PERF-006)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Đo phân vị thời gian phản hồi và thời gian từng bước khi hỏi tuần tự |
| Truy vết | BR-011, AC-011, US-013, LG-05, T3-06 |
| Ưu tiên | Cao |
| Điều kiện trước | Tài liệu của bộ câu hỏi đã `ready` cho tài khoản đánh giá; bộ nhớ đệm đã "làm nóng" bằng 3 câu hỏi |
| Dữ liệu | `evaluation/datasets/v1.jsonl` (hoặc bộ chuẩn đã duyệt) |
| Công cụ | `evaluation/run_eval.py --api …` (độ trễ đầu-cuối phía client), Prometheus (theo bước) |

**Các bước**
1. Chạy bộ đánh giá với `--config-note` mô tả cấu hình.
2. Trong Prometheus: `histogram_quantile(0.5|0.9|0.95, sum(rate(qa_step_seconds_bucket[1h])) by (le, step))`.

**Kết quả mong đợi**
- Báo cáo có p50 / p90 / p95 / max (ms); không có lỗi gọi.
- p90 ≤ [TBD: OQ-002] (tham chiếu đề xuất: 15 s); bước `embed` + `retrieve` < 1 s ở p95.
- Ghi số liệu và chi phí vào `docs/implement/tuning_log.md`.
