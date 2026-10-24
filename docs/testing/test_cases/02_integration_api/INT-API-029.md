# INT-API-029 — Xóa vĩnh viễn

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Worker xóa toàn bộ chunk, tệp trên kho, đoạn trích nguyên văn trong citation; đặt `deleted` và `purged_at` |
| Truy vết | BR-024, AC-024, US-007, T3-02, LG-08 |
| Ưu tiên / Loại | Cao / Dương |
| Tự động hóa | `test_delete_and_purge.py::test_purge_removes_chunks_file_and_sets_purged_at` |

**Các bước**
1. Hỏi một câu có nguồn từ `DuAn.pdf`; ghi lại `storage_key`.
2. `DELETE`; chạy worker.
3. Đọc `documents`, `chunks`, `citations`; kiểm khóa trên kho; `GET` lịch sử hội thoại.

**Kết quả mong đợi**
- `status = "deleted"`, `purged_at` khác null; 0 chunk; khóa không còn trên kho.
- Citation còn tên tài liệu và số trang nhưng `cited_text = null` (cả trong lịch sử trả về).
