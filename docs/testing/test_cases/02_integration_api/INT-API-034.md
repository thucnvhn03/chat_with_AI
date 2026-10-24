# INT-API-034 — Báo cáo sử dụng theo tuần

Nhóm: [02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Đếm người dùng hoạt động (chỉ BD) và số câu hỏi theo tuần ISO, đúng khoảng; tỷ lệ hữu ích từ đánh giá |
| Truy vết | BR-016, BR-021, BR-017, AC-016, AC-021, US-022..024, T4-02 |
| Ưu tiên / Loại | Trung bình / Dương |
| Tự động hóa | `test_admin_reports_health.py::test_weekly_usage_with_seed_data`, `test_usage_endpoint_includes_helpful_ratio` |

**Các bước**
1. Dữ liệu hạt giống (hôm nay = 22/10/2026): tuần này 2 người, 3 câu hỏi; tuần trước 3 người, 1 câu hỏi; 1 câu hỏi cách 6 tuần; 1 `access_denied`. Gọi `weekly_usage(4)`.
2. "an" hỏi 3 câu, đánh giá hữu ích, hữu ích, không hữu ích; "quanly" (manager) `GET /reports/usage?weeks=4`; "an" gọi cùng endpoint.

**Kết quả mong đợi**
- Bước 1: 4 tuần, (hoạt động, câu hỏi) = (0,0), (0,0), (3,1), (2,3); tỷ lệ hữu ích null.
- Bước 2: tuần hiện tại `active_users = 1` (quản lý không được tính), `questions = 3`, `helpful_ratio ≈ 0,667`, `feedback_count = 3`; "an" nhận 403.
