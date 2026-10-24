# T1-07 · Màn hình S-05 Quản lý quyền

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-017 — Chỉ người được cấp quyền mới dùng được ứng dụng (P0) |
| Loại việc | FE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-05, T1-06 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** dựng S-05 theo `S-05-quan-ly-quyen.html` và ảnh `s05-default`, `s05-confirm`, `s05-empty`: biểu mẫu cấp quyền, bảng người dùng, thu hồi có xác nhận, trạng thái trống. Cột "Phạm vi tài liệu" hiển thị `[TBD: OQ-003]` cho tới khi có quyết định.
- **Xong khi:** thao tác cấp và thu hồi chạy với backend thật; thu hồi phải qua bước xác nhận; kiểm thử cho ba trạng thái.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
