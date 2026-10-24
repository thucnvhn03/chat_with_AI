# INT-API-006 — Người bị thu hồi mất truy cập ngay

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Sau khi quản trị bảo mật thu hồi quyền, yêu cầu kế tiếp của người đó bị từ chối; đăng nhập lại cũng bị từ chối |
| Truy vết | BR-014, AC-014, LG-07, T1-04, T1-05 |
| Ưu tiên / Loại | Cao / Bảo mật |
| Điều kiện trước | "an" (bd) và "admin" (security_admin) đã đăng nhập trên hai client |
| Tự động hóa | `test_auth.py::test_revoked_user_loses_access_on_next_request` |

**Các bước**
1. "an": `GET /documents` → 200.
2. "admin": `DELETE /admin/access/{id của an}`.
3. "an": `GET /documents`.
4. "an": `POST /auth/login` lại.

**Kết quả mong đợi**
- Bước 2: 204. Bước 3: 401 hoặc 403. Bước 4: 403 `no_access`.
