# INT-API-035 — Quản lý quyền truy cập

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Cấp quyền (tạo người dùng nếu chưa có), liệt kê, thu hồi (giữ bản ghi); vai trò sai bị từ chối; không tự thu hồi; vai trò khác không gọi được |
| Truy vết | BR-014, US-017, T1-05 |
| Ưu tiên / Loại | Cao / Dương, âm |
| Tự động hóa | `test_auth.py::test_admin_grant_list_revoke`, `test_admin_cannot_revoke_self`, `test_admin_endpoints_forbidden_for_other_roles` |

**Các bước**
1. "admin": `POST /admin/access` `{"login": "moi.nguoi", "role": "manager"}`.
2. `GET /admin/access`.
3. `DELETE /admin/access/{moi.nguoi}`; `GET`.
4. `POST` với `role = "root"`.
5. `DELETE` chính mình.
6. Người `bd` và `manager` gọi `GET` và `POST`.

**Kết quả mong đợi**
- 201, `status = "active"`; danh sách {admin, moi.nguoi}; sau thu hồi: `revoked`, `revoked_at` có giá trị; 400; 409 `cannot_revoke_self`; 403.
