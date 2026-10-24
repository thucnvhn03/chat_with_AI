# INT-API-003 — Đăng nhập đúng nhưng chưa được cấp quyền

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Người chưa có `access_grants` đang hoạt động bị từ chối, không được cấp phiên |
| Truy vết | BR-014, AC-014, US-017, T1-04 |
| Ưu tiên / Loại | Cao / Âm |
| Điều kiện trước | Người dùng "khach" có mật khẩu, không có quyền |
| Tự động hóa | `test_auth.py::test_login_without_grant_is_no_access` |

**Các bước**
1. `POST /auth/login` cho "khach".

**Kết quả mong đợi**
- 403, `error.code = "no_access"`; không có header `Set-Cookie`.
