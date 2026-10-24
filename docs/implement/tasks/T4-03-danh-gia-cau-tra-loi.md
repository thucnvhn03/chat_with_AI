# T4-03 · Đánh giá câu trả lời

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 4 — Chất lượng, đo lường, sẵn sàng phát hành |
| Story | US-024 — Đánh giá câu trả lời (P2) |
| Loại việc | BE+FE |
| Cỡ | S (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T2-08 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:**
  - **BE:** `PUT /messages/{id}/feedback` (`{value: helpful|not_helpful}`; chỉ chủ hội thoại; ghi đè được); phát `answer_feedback_submitted`.
  - **FE:** `FeedbackControl` (C-13) với `aria-pressed`, hai nút "Hữu ích" / "Không hữu ích".
- **Xong khi:** đánh giá được lưu, đổi lại được, và hiện trong tổng hợp ở T4-02 (AC-017).

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G3 (trước Sprint 4): OQ-002 (ngưỡng), bộ câu hỏi chuẩn đầy đủ. | Cổng G4 (cuối Sprint 4): tiêu chí launch LG-01..LG-11 đạt, hoặc có quyết định ngoại lệ bằng văn bản của sponsor.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
