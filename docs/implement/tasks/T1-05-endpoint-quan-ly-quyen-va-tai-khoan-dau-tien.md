# T1-05 · Endpoint quản lý quyền và tài khoản đầu tiên

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-017 — Chỉ người được cấp quyền mới dùng được ứng dụng (P0) |
| Loại việc | BE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-04 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** `GET /admin/access`, `POST /admin/access` (`{login, role}`; tạo `users` nếu chưa có), `DELETE /admin/access/{user_id}` (đặt `revoked`, không xóa bản ghi); chỉ vai trò `security_admin`. Lệnh quản trị `python -m app.cli create-admin <login>` tạo tài khoản quản trị bảo mật đầu tiên.
- **Xong khi:** kiểm thử: vai trò khác gọi → 403; thu hồi xong người đó không đăng nhập hoặc không gọi API được; lệnh `create-admin` chạy được trên cơ sở dữ liệu trống.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
