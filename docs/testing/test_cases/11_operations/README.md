# 11 — Ca kiểm thử vận hành và sẵn sàng (OPS-001..OPS-005)

Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md) mục 6.1.12. Tham chiếu: `docs/implement/ops_runbook.md`, `deploy/monitoring/`. Môi trường: Docker Compose (Local) cho OPS-001..003; Test/Staging cho OPS-004, OPS-005.

> Lưu ý tài nguyên: chạy trên máy đủ tài nguyên. Trên máy phát triển 8 GB RAM, giới hạn bộ nhớ máy ảo Docker (ví dụ `.wslconfig` `memory=4GB`) và dùng cấu hình embedding giả lập.

## Danh sách ca (5)

| Mã ca | Tên |
|---|---|
| [OPS-001](OPS-001.md) | Health báo lỗi khi một thành phần dừng |
| [OPS-002](OPS-002.md) | Luật cảnh báo phát đúng |
| [OPS-003](OPS-003.md) | Theo dõi tài liệu xóa quá hạn |
| [OPS-004](OPS-004.md) | Triển khai theo tài liệu vận hành |
| [OPS-005](OPS-005.md) | Khôi phục sao lưu không "hồi sinh" tài liệu đã xóa |
