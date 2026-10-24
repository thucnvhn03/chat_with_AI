# T2-04 · Điều phối hỏi đáp: ba lớp từ chối và ánh xạ nguồn

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 2 — Hỏi đáp có nguồn |
| Story | US-008 — Đặt câu hỏi bằng ngôn ngữ tự nhiên (P0); US-009 — Câu trả lời tổng hợp từ nhiều tài liệu (P0); US-011 — Báo rõ khi tài liệu không có thông tin (P0); US-014 — Biết câu trả lời lấy từ tài liệu nào (P0) |
| Loại việc | BE |
| Cỡ | L (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T2-02, T2-03 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** `modules/qa/service.py` thực hiện mục 5.3 của plan: nhúng câu hỏi → truy xuất → (1) điểm cao nhất < `MIN_RELEVANCE_SCORE` hoặc không có chunk → `not_found`, **không gọi mô hình**; (2) mô hình trả câu từ chối cố định → `not_found`; (3) có nội dung nhưng không có citation hợp lệ → `not_found`. Ánh xạ citation → `document_id`, `document_name`, `page`; gộp trùng; trả `latency_ms`.
- **Xong khi:** kiểm thử đơn vị với `fake_llm`: ba lớp từ chối đều cho `not_found=true`; câu trả lời có nội dung luôn có ≥ 1 citation; thứ tự và số trang của citation đúng.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G1 (trước Sprint 2): OQ-006 (kịch bản A/B), OQ-005 sơ bộ, OQ-007. Chưa có thì dùng Kịch bản A với dữ liệu mẫu không nhạy cảm.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
