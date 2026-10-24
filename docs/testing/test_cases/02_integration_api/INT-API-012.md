# INT-API-012 — Tài liệu bị xóa trong lúc đang nạp

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Nếu tài liệu chuyển `deleting` giữa chừng, worker bỏ kết quả, không ghi chunk |
| Truy vết | BR-005, implement_plan 5.1 bước 7, T1-15 |
| Ưu tiên / Loại | Cao / Đồng thời |
| Tự động hóa | `test_ingestion_flow.py::test_document_moved_to_deleting_during_ingest_is_discarded` |

**Các bước**
1. Tải HĐ-3T.
2. Thay hàm nhúng để đặt tài liệu sang `deleting` trước khi trả vector.
3. Chạy worker.

**Kết quả mong đợi**
- Tài liệu vẫn `deleting`; số chunk = 0.
