# INT-API-039 — Migration và ràng buộc lược đồ

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Migration lên/xuống thành công; ràng buộc CHECK, UNIQUE, NOT NULL, CASCADE hoạt động |
| Truy vết | T0-10, T1-01, T1-09, T2-01, BR-019 |
| Ưu tiên / Loại | Cao / Dương, âm |
| Tự động hóa | `test_migrations.py` (8 kiểm thử) |

**Các bước**
1. `downgrade base` → chỉ còn `alembic_version`; `upgrade head` → đủ 14 bảng.
2. Chèn `access_grants` với vai trò "admin" / trạng thái "paused".
3. Chèn hai `users` cùng `login`.
4. Chèn `documents` trạng thái "archived"; cập nhật `failure_reason = "virus"`.
5. Chèn `chunks` thiếu `page`.
6. Chèn `jobs` với `kind = "email"`.
7. Xóa `messages` có `citations` và `feedback`.

**Kết quả mong đợi**
- Bước 1 thành công. Bước 2–6: `IntegrityError`. Bước 7: citation và đánh giá bị xóa theo (CASCADE).
