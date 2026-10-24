# INT-API-004 — Bảo vệ CSRF theo Origin

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Yêu cầu thay đổi dữ liệu không có `Origin` hợp lệ bị từ chối |
| Truy vết | implement_plan 10.5, T1-04 |
| Ưu tiên / Loại | Cao / Bảo mật |
| Tự động hóa | `test_auth.py::test_post_without_valid_origin_is_rejected` |

**Các bước**
1. `POST /auth/login` không có header `Origin`.
2. Gửi với `Origin: https://evil.example`.
3. Gửi với `Origin: http://localhost:5173`.

**Kết quả mong đợi**
- Bước 1, 2: 403, `error.code = "csrf_rejected"`.
- Bước 3: 200.
