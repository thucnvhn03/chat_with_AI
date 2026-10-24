# T1-06 · Màn hình S-01 Đăng nhập và AuthGate

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-017 — Chỉ người được cấp quyền mới dùng được ứng dụng (P0) |
| Loại việc | FE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T0-05, T1-04 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** dựng S-01 theo `html_design/S-01-dang-nhap.html` và ảnh `s01-default`, `s01-wrong`, `s01-noaccess`, `s01-expired`: bốn trạng thái từ mã lỗi 401/403 của API. `AuthGate` (C-01): kiểm tra `/auth/me`; 401 → điều hướng `/login` và lưu tạm câu hỏi đang soạn trong `sessionStorage`. Điều hướng sau đăng nhập: `bd` → `/`, `security_admin` → `/admin/access`, `manager` → `/reports`.
- **Xong khi:** kiểm thử Testing Library cho cả bốn trạng thái; E2E: đăng nhập đúng, sai, không có quyền, hết phiên; axe không có lỗi nghiêm trọng.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
