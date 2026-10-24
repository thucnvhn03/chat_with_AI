# T2-03 · Cổng sinh câu trả lời và adapter Claude

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 2 — Hỏi đáp có nguồn |
| Story | US-008 — Đặt câu hỏi bằng ngôn ngữ tự nhiên (P0) |
| Loại việc | BE |
| Cỡ | L (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-08, T1-15 |
| Trạng thái | Review (kiểm thử với phản hồi giả lập đạt; kiểm thử API thật chờ khóa) |

- **Làm gì:** `ports/ai.py` thêm `SourceChunk`, `GeneratedAnswer`, `AnswerGenerator` (mục 6.4 của plan). `adapters/claude_llm.py`:
  1. Mỗi chunk là một khối `document` văn bản bật `citations`, tiêu đề "tên tệp — trang N".
  2. Mô hình `ANSWER_MODEL` (mặc định `claude-opus-5-5`); đặt `effort` từ `ANSWER_EFFORT`; **không** đặt `thinking`; **không** dùng prefill; **không** dùng `output_config.format` (xung đột với citations).
  3. Chỉ dẫn hệ thống ở mục 5.3 của plan, có `cache_control`.
  4. Đọc `stop_reason` trước nội dung: `refusal` → `refused=True`; `max_tokens` → coi là lỗi.
  5. Bật chuyển mô hình dự phòng phía máy chủ khi bị từ chối (xác nhận cách truyền tham số theo phiên bản SDK đã cài).
  6. `timeout`, `max_retries`; bắt lỗi theo thứ tự `RateLimitError` → `APIStatusError` → `APIConnectionError`.
  7. Một adapter giả lập `fake_llm.py` trả citation định sẵn, dùng cho kiểm thử.
- **Xong khi:** kiểm thử đơn vị với phản hồi SDK được giả lập: citation được ánh xạ đúng chỉ số chunk; `refusal` xử lý đúng; kiểm thử có đánh dấu "cần khóa API" chạy thật trên dữ liệu mẫu ở môi trường kiểm thử.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G1 (trước Sprint 2): OQ-006 (kịch bản A/B), OQ-005 sơ bộ, OQ-007. Chưa có thì dùng Kịch bản A với dữ liệu mẫu không nhạy cảm.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
