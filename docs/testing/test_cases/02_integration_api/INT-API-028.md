# INT-API-028 — Xóa loại tài liệu khỏi truy vấn ngay lập tức

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Sau `DELETE`, câu hỏi chỉ có đáp án trong tài liệu đó nhận "không tìm thấy" **trước khi** worker xóa vĩnh viễn chạy |
| Truy vết | BR-005, AC-005, US-006, T3-01 |
| Ưu tiên / Loại | Cao / Dương |
| Dữ liệu | `DuAn.pdf`: "Mật mã dự án Hải Đăng là XANH-LAM-42 dùng cho buổi trình bày với đối tác." |
| Tự động hóa | `test_delete_and_purge.py::test_deleted_document_is_excluded_immediately` |

**Các bước**
1. Hỏi "Mật mã dự án Hải Đăng là gì?" → có câu trả lời.
2. `DELETE /documents/{id}`.
3. Không chạy worker; kiểm bảng `chunks`.
4. Hỏi lại; `GET /documents`; `GET /documents/{id}`; `GET /documents/{id}/pages/1`.

**Kết quả mong đợi**
- Bước 2: 202, `status = "deleting"`.
- Bước 3: chunk vẫn còn.
- Bước 4: `not_found = true`; danh sách rỗng; 404; 404.
