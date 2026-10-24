# T2-07 · FE: khung hội thoại và ô nhập

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 2 — Hỏi đáp có nguồn |
| Story | US-008 — Đặt câu hỏi bằng ngôn ngữ tự nhiên (P0) |
| Loại việc | FE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-18, T2-05 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** `ChatPanel` (C-07), `MessageList` (C-08), `QuestionInput` (C-09) khớp ảnh `s02-default`: gửi bằng nút và Ctrl/Cmd+Enter; ô nhập vô hiệu kèm giải thích khi chưa có tài liệu `ready` (`s02-empty`); kiểm tra độ dài `[TBD: PQ-002]`; trạng thái "Đang xử lý câu hỏi…" xuất hiện ngay khi gửi.
- **Xong khi:** kiểm thử cho các trạng thái trống, mặc định, đang chờ; vô hiệu hóa đúng; focus quay về ô nhập sau khi có câu trả lời.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G1 (trước Sprint 2): OQ-006 (kịch bản A/B), OQ-005 sơ bộ, OQ-007. Chưa có thì dùng Kịch bản A với dữ liệu mẫu không nhạy cảm.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
