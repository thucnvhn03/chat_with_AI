# T4-08 · Rà soát khả năng tiếp cận toàn bộ

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 4 — Chất lượng, đo lường, sẵn sàng phát hành |
| Story | Nền tảng / nghiệm thu (không gắn riêng một story) |
| Loại việc | QA |
| Cỡ | S (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T4-02, T4-03 |
| Trạng thái | Review (axe tự động không có vi phạm nghiêm trọng; còn kiểm thủ công với trình đọc màn hình) |

- **Làm gì:** axe tự động cho S-01..S-07 và mọi trạng thái; kiểm tra thủ công: chỉ dùng bàn phím, trình đọc màn hình, tương phản, thu phóng 200%.
- **Xong khi:** không còn vi phạm mức nghiêm trọng hoặc cao; danh sách vi phạm nhỏ còn lại có chủ và hạn.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G3 (trước Sprint 4): OQ-002 (ngưỡng), bộ câu hỏi chuẩn đầy đủ. | Cổng G4 (cuối Sprint 4): tiêu chí launch LG-01..LG-11 đạt, hoặc có quyết định ngoại lệ bằng văn bản của sponsor.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
