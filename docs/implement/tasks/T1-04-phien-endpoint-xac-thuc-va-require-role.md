# T1-04 · Phiên, endpoint xác thực và `require_role`

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-017 — Chỉ người được cấp quyền mới dùng được ứng dụng (P0) |
| Loại việc | BE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-02 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:**
  1. Phiên lưu phía máy chủ, cookie `HttpOnly; Secure; SameSite=Lax`, hết hạn sau `SESSION_IDLE_HOURS` không hoạt động.
  2. `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` (`{user, role}`).
  3. Phụ thuộc FastAPI `current_user` và `require_role(*roles)`: 401 `session_expired` khi hết phiên, 403 `no_access` khi chưa được cấp quyền hoặc đã `revoked`, 403 `forbidden_role` khi sai vai trò.
  4. Bảo vệ CSRF (kiểm tra header `Origin` hoặc token) cho yêu cầu thay đổi dữ liệu.
  5. Phát sự kiện `session_started` và `access_denied` vào `usage_events` (bảng tạo ở T2-01 — tạm ghi log, bổ sung ghi bảng khi T2-01 xong).
- **Xong khi:** kiểm thử tích hợp: không có phiên → 401; người `revoked` → 403 ở yêu cầu kế tiếp (AC-014); thiếu `Origin` hợp lệ khi `POST` → bị từ chối.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
