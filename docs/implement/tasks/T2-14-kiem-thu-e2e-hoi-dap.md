# T2-14 · Kiểm thử E2E hỏi đáp

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 2 — Hỏi đáp có nguồn |
| Story | US-008 — Đặt câu hỏi bằng ngôn ngữ tự nhiên (P0) |
| Loại việc | QA |
| Cỡ | S (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T2-09, T2-10, T2-12 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** Playwright với backend dùng `fake_llm`: tải PDF → hỏi → thấy câu trả lời kèm nguồn → chọn nguồn mở S-03 đúng trang → hỏi ngoài phạm vi thấy "không tìm thấy" → mất mạng khi hỏi. axe trên S-02 và S-03.
- **Xong khi:** các kịch bản đạt; phủ AC-006, AC-009, AC-012, AC-019 ở tầng giao diện.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G1 (trước Sprint 2): OQ-006 (kịch bản A/B), OQ-005 sơ bộ, OQ-007. Chưa có thì dùng Kịch bản A với dữ liệu mẫu không nhạy cảm.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
