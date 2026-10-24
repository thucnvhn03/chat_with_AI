# INT-API-026 — Trang nguồn: trang không hợp lệ và quyền

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Trang ngoài khoảng và tài liệu của người khác trả 404 |
| Truy vết | BR-019, BR-020, US-015, T2-06 |
| Ưu tiên / Loại | Cao / Âm |
| Tự động hóa | `test_qa_flow.py::test_source_page_and_file_access` |

**Các bước**
1. `GET /documents/{HĐ}/pages/4`, `/pages/0`.
2. "binh": `GET /documents/{HĐ của an}/pages/1`, `/file`.

**Kết quả mong đợi**
- Tất cả 404.
