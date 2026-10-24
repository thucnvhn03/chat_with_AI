# INT-API-038 — Lệnh tạo quản trị viên đầu tiên

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | `python -m app.cli create-admin <login>` chạy trên cơ sở dữ liệu trống, tạo tài khoản quản trị bảo mật đăng nhập được |
| Truy vết | US-017, T1-05 |
| Ưu tiên / Loại | Trung bình / Dương |
| Tự động hóa | `test_auth.py::test_cli_create_admin_on_empty_database` |

**Các bước**
1. Đặt `INITIAL_PASSWORD`; chạy `create-admin quan.tri`.
2. Xác thực "quan.tri" với mật khẩu đó; đọc vai trò.

**Kết quả mong đợi**
- Xác thực thành công; vai trò `security_admin`.
