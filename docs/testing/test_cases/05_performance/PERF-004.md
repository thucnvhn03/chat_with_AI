# PERF-004 — Truy xuất trong kho lớn có lọc quyền

Nhóm: [05 — Ca kiểm thử hiệu năng (PERF-001..PERF-006)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Truy vấn pgvector có lọc `allowed_document_ids` vẫn nhanh và đủ `TOP_K` khi kho lớn |
| Truy vết | implement_plan 5.2, T2-02 |
| Ưu tiên | Trung bình |
| Dữ liệu | Kho [Đề xuất: 10.000 chunk] của nhiều người dùng; người dùng thử có 5 tài liệu |

**Các bước**
1. Sinh dữ liệu (có thể dùng embedding giả lập để tạo nhanh).
2. Chạy 100 truy vấn ngẫu nhiên của người dùng thử; đo thời gian bước `retrieve`; chạy `EXPLAIN ANALYZE` một truy vấn mẫu.

**Kết quả mong đợi**
- Mọi truy vấn trả đủ `TOP_K` (hoặc đủ số chunk hiện có) và chỉ thuộc 5 tài liệu được phép.
- p95 bước `retrieve` ≤ [Đề xuất: 300 ms]; kế hoạch truy vấn dùng chỉ mục HNSW.
