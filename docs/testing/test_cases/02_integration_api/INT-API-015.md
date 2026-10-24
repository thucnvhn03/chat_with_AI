# INT-API-015 — Truy xuất không bao giờ trả tài liệu ngoài phạm vi

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Bộ lọc quyền nằm trong câu truy vấn: chunk của tài liệu không thuộc danh sách được phép không xuất hiện, kể cả khi giống câu hỏi hơn |
| Truy vết | BR-020, AC-020, ADR-004, T2-02 |
| Ưu tiên / Loại | Cao / Bảo mật |
| Tự động hóa | `test_retrieval.py::test_chunks_outside_allowed_documents_never_appear`, `test_empty_allowed_set` |

**Các bước**
1. Tạo tài liệu "mine" (1 chunk) và "other" (5 chunk cùng nội dung).
2. Truy xuất với danh sách được phép = {mine}.
3. Truy xuất với danh sách rỗng.

**Kết quả mong đợi**
- Bước 2: mọi kết quả thuộc "mine". Bước 3: danh sách rỗng.
