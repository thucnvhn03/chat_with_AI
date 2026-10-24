# T0-08 · Spike sinh câu trả lời có trích dẫn

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 0 — Nền tảng và spike |
| Story | Nền tảng / nghiệm thu (không gắn riêng một story) |
| Loại việc | SPK |
| Cỡ | S (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-07; dữ liệu **không nhạy cảm**; khóa API (không commit) |
| Trạng thái | Blocked (mã xong; chưa chạy vì chưa có ANTHROPIC_API_KEY) |

- **Làm gì:** script gọi Claude (`claude-opus-5-5`, SDK `anthropic`) với các chunk là khối `document` bật `citations` (phác thảo ở `implement_plan.md` mục 6.4). Kiểm: (a) citation trỏ đúng chunk (`document_index`); (b) câu hỏi ngoài phạm vi có nhận câu từ chối cố định không; (c) `effort` `low` so với `medium`; (d) `usage.cache_read_input_tokens` ở lượt thứ hai.
- **Sản phẩm:** `evaluation/spikes/generate.py` và `docs/implement/spike_generation.md`.
- **Xong khi:** báo cáo xác nhận ánh xạ citation → trang hoạt động; nêu `ANSWER_EFFORT` khởi điểm; ghi chi phí mỗi câu hỏi mẫu (đầu vào RSK-005).

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G0 (cuối Sprint 0): chốt bộ công nghệ, DQ-003, kết quả ba spike.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
