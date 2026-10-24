# 06 — Ca kiểm thử bảo mật (SEC-001..SEC-013)

Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md) mục 6.1.7. Môi trường: kiểm thử tích hợp (PostgreSQL, S3 thật) cho các ca tự động; Test/Staging cho ca thủ công và quét động. Thư mục: `backend/tests/security/`, `backend/tests/integration/`.

Các ca SEC-001 và SEC-003 **tự sinh danh sách route từ OpenAPI**, nên route mới được kiểm tự động; mỗi ca có thêm một kiểm thử chứng minh nó phát hiện được route thiếu bảo vệ.

## Danh sách ca (13)

| Mã ca | Tên |
|---|---|
| [SEC-001](SEC-001.md) | Mọi route yêu cầu phiên |
| [SEC-002](SEC-002.md) | Phân quyền theo vai trò |
| [SEC-003](SEC-003.md) | Cô lập dữ liệu giữa người dùng |
| [SEC-004](SEC-004.md) | Chính sách mật khẩu và khóa tạm |
| [SEC-005](SEC-005.md) | Quản lý phiên |
| [SEC-006](SEC-006.md) | Chống CSRF |
| [SEC-007](SEC-007.md) | Chống XSS từ nội dung câu trả lời |
| [SEC-008](SEC-008.md) | Tiêu đề bảo mật của frontend production |
| [SEC-009](SEC-009.md) | Không lộ thông tin qua lỗi |
| [SEC-010](SEC-010.md) | Log và sự kiện không chứa nội dung (canary) |
| [SEC-011](SEC-011.md) | Kiểm tra tệp tải lên theo nội dung |
| [SEC-012](SEC-012.md) | Quét lỗ hổng phụ thuộc |
| [SEC-013](SEC-013.md) | Dữ liệu gửi ra dịch vụ AI |
