# INT-API-017 — Đủ TOP_K khi danh sách được phép nhỏ trong kho lớn

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Với chỉ mục HNSW và `hnsw.iterative_scan`, lọc theo danh sách nhỏ vẫn trả đủ `TOP_K` |
| Truy vết | implement_plan 5.2, T2-02 |
| Ưu tiên / Loại | Trung bình / Biên |
| Tự động hóa | `test_retrieval.py::test_small_allowed_set_in_large_store_still_returns_top_k` |

**Các bước**
1. Tạo 60 tài liệu nhiễu × 10 chunk rất giống câu hỏi; 1 tài liệu được phép × 12 chunk không liên quan.
2. Truy xuất "báo giá dịch vụ vận chuyển", `top_k = 8`, chỉ tài liệu được phép.

**Kết quả mong đợi**
- Đúng 8 kết quả, đều thuộc tài liệu được phép.
