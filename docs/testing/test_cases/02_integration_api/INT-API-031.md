# INT-API-031 — Quyền xóa tài liệu

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Người khác không xóa được (404); quản lý không có quyền (403); quản trị bảo mật xóa được mọi tài liệu |
| Truy vết | BR-020, US-006, T3-01 |
| Ưu tiên / Loại | Cao / Bảo mật |
| Tự động hóa | `test_delete_and_purge.py::test_delete_permissions` |

**Các bước**
1. "binh" (bd): `DELETE` tài liệu của "an".
2. "quanly" (manager): `DELETE`.
3. "admin" (security_admin): `DELETE` hai lần.

**Kết quả mong đợi**
- 404; 403; 202 rồi 404.
