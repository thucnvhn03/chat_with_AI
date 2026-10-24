# INT-API-008 — Giới hạn số tài liệu mỗi người

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Tệp vượt `MAX_DOCS_PER_USER` bị từ chối với lý do riêng |
| Truy vết | BR-002, US-002, T1-11 |
| Ưu tiên / Loại | Trung bình / Biên |
| Điều kiện trước | `MAX_DOCS_PER_USER = 2` |
| Tự động hóa | `test_ingestion_flow.py::test_max_docs_per_user` |

**Các bước**
1. `POST /documents` với 3 PDF hợp lệ.

**Kết quả mong đợi**
- `failure_reason` lần lượt: null, null, `too_many_documents`.
