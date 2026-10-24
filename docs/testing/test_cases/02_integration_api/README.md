# 02 — Ca kiểm thử tích hợp API (INT-API-001..INT-API-040)

Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md) mục 6.1.2. Môi trường: Local/CI với PostgreSQL 16 + pgvector và kho S3 thật; adapter AI giả lập; embedding giả lập; FastAPI TestClient gửi `Origin: http://localhost:5173`. Mỗi kiểm thử bắt đầu với cơ sở dữ liệu trống. Thư mục kiểm thử: `backend/tests/integration/`.

Ký hiệu dữ liệu dùng lại:
- **HĐ-3T** — PDF 3 trang: (1) "Hợp đồng phân phối số 12/2026 giữa Công ty An Bình và Công ty Minh Long."; (2) "Điều 3. Thời hạn thanh toán là 30 ngày kể từ ngày nhận hóa đơn hợp lệ."; (3) "Điều 7. Phạt chậm thanh toán là 0,05% mỗi ngày trên số tiền chậm trả."
- **BG-2T** — PDF 2 trang: (1) "Bảng báo giá dịch vụ lưu kho năm 2026."; (2) "Giá gói tiêu chuẩn là 12 triệu đồng mỗi tháng, đã gồm bảo hiểm hàng hóa."
- **Người dùng BD "an"** — tài khoản có vai trò `bd`, đã đăng nhập.

## Danh sách ca (40)

| Mã ca | Tên |
|---|---|
| [INT-API-001](INT-API-001.md) | Đăng nhập thành công |
| [INT-API-002](INT-API-002.md) | Sai thông tin đăng nhập không tiết lộ tài khoản |
| [INT-API-003](INT-API-003.md) | Đăng nhập đúng nhưng chưa được cấp quyền |
| [INT-API-004](INT-API-004.md) | Bảo vệ CSRF theo Origin |
| [INT-API-005](INT-API-005.md) | Phiên hết hạn |
| [INT-API-006](INT-API-006.md) | Người bị thu hồi mất truy cập ngay |
| [INT-API-007](INT-API-007.md) | Tải nhiều tệp, mỗi tệp xét độc lập |
| [INT-API-008](INT-API-008.md) | Giới hạn số tài liệu mỗi người |
| [INT-API-009](INT-API-009.md) | Nạp PDF hợp lệ tới trạng thái sẵn sàng |
| [INT-API-010](INT-API-010.md) | Lý do lỗi do worker xác định |
| [INT-API-011](INT-API-011.md) | Lỗi tạm thời được thử lại rồi chuyển failed |
| [INT-API-012](INT-API-012.md) | Tài liệu bị xóa trong lúc đang nạp |
| [INT-API-013](INT-API-013.md) | Nhiều worker không lấy trùng việc |
| [INT-API-014](INT-API-014.md) | Thử lại tài liệu lỗi |
| [INT-API-015](INT-API-015.md) | Truy xuất không bao giờ trả tài liệu ngoài phạm vi |
| [INT-API-016](INT-API-016.md) | Chỉ truy xuất tài liệu sẵn sàng |
| [INT-API-017](INT-API-017.md) | Đủ TOP_K khi danh sách được phép nhỏ trong kho lớn |
| [INT-API-018](INT-API-018.md) | Giới hạn số chunk mỗi tài liệu |
| [INT-API-019](INT-API-019.md) | Câu trả lời có nguồn đúng tài liệu và trang |
| [INT-API-020](INT-API-020.md) | Câu ngoài phạm vi không gọi mô hình |
| [INT-API-021](INT-API-021.md) | Kiểm tra độ dài câu hỏi |
| [INT-API-022](INT-API-022.md) | Dịch vụ AI từ chối hoặc quá thời gian |
| [INT-API-023](INT-API-023.md) | Mỗi câu hỏi đúng một bản ghi kiểm toán, không nội dung |
| [INT-API-024](INT-API-024.md) | Lỗi commit không bị nuốt |
| [INT-API-025](INT-API-025.md) | Lịch sử hội thoại và câu hỏi tiếp theo |
| [INT-API-026](INT-API-026.md) | Trang nguồn: trang không hợp lệ và quyền |
| [INT-API-027](INT-API-027.md) | Tải tệp gốc qua backend |
| [INT-API-028](INT-API-028.md) | Xóa loại tài liệu khỏi truy vấn ngay lập tức |
| [INT-API-029](INT-API-029.md) | Xóa vĩnh viễn |
| [INT-API-030](INT-API-030.md) | Xóa vĩnh viễn chịu lỗi và làm lại được |
| [INT-API-031](INT-API-031.md) | Quyền xóa tài liệu |
| [INT-API-032](INT-API-032.md) | Đánh giá câu trả lời |
| [INT-API-033](INT-API-033.md) | Bản ghi kiểm toán: lọc và phân trang |
| [INT-API-034](INT-API-034.md) | Báo cáo sử dụng theo tuần |
| [INT-API-035](INT-API-035.md) | Quản lý quyền truy cập |
| [INT-API-036](INT-API-036.md) | Health báo lỗi khi thành phần dừng |
| [INT-API-037](INT-API-037.md) | Đăng nhập OIDC |
| [INT-API-038](INT-API-038.md) | Lệnh tạo quản trị viên đầu tiên |
| [INT-API-039](INT-API-039.md) | Migration và ràng buộc lược đồ |
| [INT-API-040](INT-API-040.md) | Dọn dữ liệu định kỳ theo thời hạn lưu |
