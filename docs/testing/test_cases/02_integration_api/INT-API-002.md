# INT-API-002 — Sai thông tin đăng nhập không tiết lộ tài khoản

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Sai mật khẩu và tài khoản không tồn tại cho cùng phản hồi; mật khẩu băm Argon2id |
| Truy vết | BR-014, T1-02 |
| Ưu tiên / Loại | Cao / Âm, bảo mật |
| Tự động hóa | `test_auth.py::test_login_wrong_password_is_generic`, `test_local_identity_right_and_wrong_password`, `test_password_hash_is_argon2id` |

**Các bước**
1. `POST /auth/login` với mật khẩu sai cho "an".
2. `POST /auth/login` với tài khoản "ai-do" không tồn tại.
3. Đọc `users.password_hash` của "an".

**Kết quả mong đợi**
- Bước 1 và 2: cùng 401, cùng thân `{"error": {"code": "invalid_credentials", ...}}`.
- Bước 3: bắt đầu bằng `$argon2id$`, không chứa mật khẩu gốc.
