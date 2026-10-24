# INT-API-009 — Nạp PDF hợp lệ tới trạng thái sẵn sàng

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Worker trích xuất, cắt chunk, nhúng và ghi; tài liệu `ready` có chunk mang số trang và vector đúng số chiều; khóa lưu trữ đúng quy ước |
| Truy vết | BR-001, AC-001, US-001, T1-15, T1-20 |
| Ưu tiên / Loại | Cao / Dương |
| Dữ liệu | `HopDong_A.pdf` (HĐ-3T) |
| Tự động hóa | `test_ingestion_flow.py::test_valid_pdf_becomes_ready_with_paged_chunks`, `test_lifecycle_invariants`, `test_upload_events_have_no_content` |

**Các bước**
1. `POST /documents` → kết quả `processing`; `GET /documents/{id}` → `processing`.
2. Chạy worker.
3. `GET /documents/{id}`; đọc bảng `chunks`, `documents.storage_key`, `usage_events`.

**Kết quả mong đợi**
- `status = "ready"`, `page_count = 3`.
- Chunk có `page` ∈ {1, 2, 3}, mọi vector dài `EMBEDDING_DIM`.
- `storage_key = documents/{owner_id}/{document_id}.pdf`.
- Bất biến: mọi tài liệu `ready` có ≥ 1 chunk; mọi chunk có `page` trong 1..`page_count`.
- Có sự kiện `document_upload_started` và `document_upload_succeeded`.
