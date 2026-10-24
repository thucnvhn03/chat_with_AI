# INT-API-027 — Tải tệp gốc qua backend

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Tệp PDF gốc trả qua backend (không lộ đường dẫn kho), không lưu đệm |
| Truy vết | US-015, implement_plan 6.2, T2-06 |
| Ưu tiên / Loại | Trung bình / Dương |
| Tự động hóa | `test_qa_flow.py::test_source_page_and_file_access` |

**Các bước**
1. `GET /documents/{HĐ}/file`.

**Kết quả mong đợi**
- 200, `Content-Type: application/pdf`, thân bắt đầu `%PDF-`; header `Cache-Control: private, no-store`, `X-Content-Type-Options: nosniff`.
