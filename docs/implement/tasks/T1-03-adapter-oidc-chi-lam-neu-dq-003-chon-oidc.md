# T1-03 · Adapter OIDC (chỉ làm nếu DQ-003 chọn OIDC)

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-017 — Chỉ người được cấp quyền mới dùng được ứng dụng (P0) |
| Loại việc | BE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-02, G0 |
| Trạng thái | Review (đã làm sẵn sau cờ AUTH_MODE=oidc; DQ-003 tạm chọn tài khoản nội bộ) |

- **Làm gì:** `adapters/oidc_identity.py`: Authorization Code + PKCE; `GET /auth/oidc/login`, `GET /auth/oidc/callback`; ánh xạ `sub`/email → `users.login`; **vai trò không lấy từ IdP** mà từ `access_grants`.
- **Xong khi:** kiểm thử với một IdP giả (mock server): đăng nhập thành công tạo/khớp `users`, người không có `access_grants` nhận 403 `no_access`. Nếu DQ-003 = tài khoản nội bộ, đánh dấu task "Won't do" và ghi lý do.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
