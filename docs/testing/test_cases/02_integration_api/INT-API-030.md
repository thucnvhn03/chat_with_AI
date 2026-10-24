# INT-API-030 — Xóa vĩnh viễn chịu lỗi và làm lại được

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Lỗi kho tệp giữa chừng được thử lại tới khi xong; chạy xóa hai lần không lỗi; tài liệu `deleting` quá hạn được đếm |
| Truy vết | BR-024, ADR-008, T3-02 |
| Ưu tiên / Loại | Cao / Lỗi |
| Tự động hóa | `test_delete_and_purge.py::test_storage_error_midway_is_retried_and_completes`, `test_purge_twice_is_harmless`, `test_overdue_deleting_documents_are_counted` |

**Các bước**
1. Kho tệp lỗi ở lần xóa đầu; `DELETE`; chạy worker.
2. Gọi trực tiếp bộ xử lý xóa hai lần.
3. Đặt `deleted_at` lùi 48 giờ cho tài liệu `deleting`; gọi đếm quá hạn.

**Kết quả mong đợi**
- Bước 1: kho được gọi xóa 2 lần; tài liệu `deleted`; khóa không còn.
- Bước 2: không ngoại lệ; `deleted`.
- Bước 3: trước khi lùi = 0; sau = 1.
