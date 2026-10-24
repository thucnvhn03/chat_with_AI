# 05 — Ca kiểm thử hiệu năng (PERF-001..PERF-006)

Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md) mục 6.1.6. Môi trường: Test/Staging với Claude thật và `bge-m3` (trừ PERF-005, PERF-006), giám sát Prometheus bật (`--profile monitoring`). Máy chạy: theo kế hoạch mục 11.3 (≥ 16 GB RAM khi dùng `bge-m3`).

**Ngưỡng:** [TBD: OQ-002] cho LG-05. Cho tới khi chốt, ca kiểm thử **báo cáo số đo** và so với giá trị tham chiếu `[Đề xuất]` ghi trong từng ca. Không đo trên máy phát triển đang chạy nhiều dịch vụ khác.

**Số liệu dùng chung:** `answer_latency_seconds` (thời gian trả lời), `qa_step_seconds{step=embed|retrieve|generate}`, `http_request_duration_seconds`, `ingest_duration_seconds`, `jobs_queued`, `jobs_oldest_queued_age_seconds`, `answers_total{outcome}`.

## Danh sách ca (6)

| Mã ca | Tên |
|---|---|
| [PERF-001](PERF-001.md) | Độ trễ hỏi đáp trên bộ câu hỏi chuẩn |
| [PERF-002](PERF-002.md) | Tải nhẹ hỏi đáp đồng thời |
| [PERF-003](PERF-003.md) | Thời gian nạp tài liệu |
| [PERF-004](PERF-004.md) | Truy xuất trong kho lớn có lọc quyền |
| [PERF-005](PERF-005.md) | Phản hồi giao diện |
| [PERF-006](PERF-006.md) | Hết thời gian chờ đúng hạn |
