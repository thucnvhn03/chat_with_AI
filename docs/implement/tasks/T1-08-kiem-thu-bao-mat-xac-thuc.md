# T1-08 · Kiểm thử bảo mật xác thực

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-017 — Chỉ người được cấp quyền mới dùng được ứng dụng (P0) |
| Loại việc | QA |
| Cỡ | S (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-04, T1-05 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** kiểm thử tự động liệt kê **mọi route** của ứng dụng (từ OpenAPI) và khẳng định: mọi route trừ `/auth/login`, `/auth/oidc/*`, `/health/*` trả 401 khi không có phiên; mọi route `/admin/*` trả 403 với `bd` và `manager`. Kiểm thử này tự mở rộng khi thêm route mới.
- **Sản phẩm:** `backend/tests/security/test_auth_matrix.py`.
- **Xong khi:** kiểm thử chạy trong CI; thêm một route chưa bảo vệ cố ý làm nó đỏ.

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
