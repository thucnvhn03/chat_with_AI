# PERF-002 — Tải nhẹ hỏi đáp đồng thời

Nhóm: [05 — Ca kiểm thử hiệu năng (PERF-001..PERF-006)](README.md) · Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md)

| Mục | Nội dung |
|---|---|
| Mục tiêu | Hệ thống giữ được độ trễ và tỷ lệ lỗi khi nhiều người hỏi cùng lúc |
| Truy vết | BR-011, ASM-002 (quy mô nhỏ), OQ-009 |
| Ưu tiên | Trung bình |
| Dữ liệu | [Đề xuất: 10] người dùng ảo, mỗi người một tài khoản BD và cùng bộ tài liệu; câu hỏi lấy ngẫu nhiên từ bộ chuẩn |
| Công cụ | k6 [Đề xuất] (đăng nhập, tạo hội thoại, gửi câu hỏi; header `Origin`) |

**Các bước**
1. Tăng dần lên 10 người trong 2 phút; giữ 15 phút; giảm về 0.
2. Theo dõi `answers_total`, `http_requests_total{status=~"5.."}`, p95.

**Kết quả mong đợi**
- p95 ≤ [TBD: OQ-002]; tỷ lệ lỗi (5xx, kể cả 504) < 1%.
- Không có lỗi giới hạn tốc độ của dịch vụ AI không được xử lý (nếu có, ghi lại để chốt hạn mức).
