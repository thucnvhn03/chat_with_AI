# INT-API-001 — Đăng nhập thành công

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Đăng nhập đúng trả thông tin người dùng, vai trò, cấu hình giao diện và cookie phiên an toàn |
| Truy vết | BR-014, AC-014, US-017, T1-04 |
| Ưu tiên / Loại | Cao / Dương |
| Điều kiện trước | Người dùng "an", vai trò `bd`, trạng thái `active` |
| Tự động hóa | `test_auth.py::test_login_me_logout` |

**Các bước**
1. `POST /auth/login` `{"login": "an", "password": "<đúng>"}`.
2. `GET /auth/me`.
3. `POST /auth/logout`, rồi `GET /auth/me`.

**Kết quả mong đợi**
- Bước 1: 200, `role = "bd"`; header `Set-Cookie` có `HttpOnly` và `SameSite=Lax` (và `Secure` khi `COOKIE_SECURE=true`).
- Bước 2: 200, `user.login = "an"`, `config.max_question_chars` > 0.
- Bước 3: 204; sau đó 401.
