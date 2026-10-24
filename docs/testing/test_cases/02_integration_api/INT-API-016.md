# INT-API-016 — Chỉ truy xuất tài liệu sẵn sàng

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Tài liệu `deleting`, `deleted`, `processing`, `failed` không bao giờ được truy xuất |
| Truy vết | BR-005, AC-005, T2-02 |
| Ưu tiên / Loại | Cao / Âm |
| Tự động hóa | `test_retrieval.py::test_only_ready_documents_are_searched` (4 trạng thái) |

**Các bước**
1. Với từng trạng thái: tạo tài liệu có chunk "điều khoản bảo mật thông tin"; truy xuất "điều khoản bảo mật".

**Kết quả mong đợi**
- Kết quả rỗng ở cả 4 trạng thái.
