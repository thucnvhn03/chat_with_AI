# T3-03 · `allowed_document_ids` và ACL

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 3 — Xóa, phạm vi quyền, kiểm toán, hội thoại |
| Story | US-018 — Chỉ thấy tài liệu trong phạm vi chia sẻ (P0) |
| Loại việc | BE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-16, T2-06; G2 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** một hàm duy nhất `modules/access/scope.py: allowed_document_ids(user) -> set[UUID]` (tài liệu của chính mình ∪ `document_acl` nếu OQ-003 cho phép chia sẻ). **Thay thế mọi chỗ** đang lọc tạm theo `owner_id` (T1-16, T2-02, T2-05, T2-06, xóa). Thêm migration `document_acl` và endpoint chia sẻ nếu OQ-003 yêu cầu; nếu chưa, bảng để trống.
- **Xong khi:** tìm kiếm trong mã không còn chỗ nào lọc quyền theo cách khác; kiểm thử T3-07 đạt.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** Cổng G2 (trước Sprint 3): OQ-003, OQ-012. Chưa có thì dùng giá trị tạm: chỉ tài liệu của chính mình; xóa ngay khi worker chạy; lưu bản ghi 365 ngày.

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
