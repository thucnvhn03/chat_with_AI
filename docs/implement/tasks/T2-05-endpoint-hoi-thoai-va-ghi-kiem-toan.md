# T2-05 · Endpoint hội thoại và ghi kiểm toán

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 2 — Hỏi đáp có nguồn |
| Story | US-008 — Đặt câu hỏi bằng ngôn ngữ tự nhiên (P0); US-014 — Biết câu trả lời lấy từ tài liệu nào (P0) |
| Loại việc | BE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T2-04, T1-04 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:**
  1. `POST /conversations`, `POST /conversations/{id}/messages` (`{question}` → `{message_id, answer, not_found, citations, latency_ms}`).
  2. Kiểm tra câu hỏi không rỗng, ≤ `MAX_QUESTION_CHARS` (400).
  3. Trước khi gọi dịch vụ AI: ghi `audit_records` (người dùng, danh sách tài liệu được phép, thời điểm) và `usage_events(question_submitted)` — **không ghi nội dung câu hỏi** vào hai bảng này.
  4. Lưu `messages` và `citations`; phát `answer_returned` (thời gian phản hồi, số nguồn, cờ `not_found`).
  5. `ANSWER_TIMEOUT_S` → 504 `answer_timeout`.
  6. Hội thoại chỉ do chủ hội thoại truy cập.
- **Xong khi:** kiểm thử tích hợp (adapter giả): mỗi câu hỏi sinh đúng một `audit_records` không chứa nội dung; người dùng khác gọi vào hội thoại → 404; câu hỏi quá dài → 400.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G1 (trước Sprint 2): OQ-006 (kịch bản A/B), OQ-005 sơ bộ, OQ-007. Chưa có thì dùng Kịch bản A với dữ liệu mẫu không nhạy cảm.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
