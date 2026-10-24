# 01 — Ca kiểm thử đơn vị (UT-001..UT-022)

Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md) mục 6.1.1. Môi trường: Local/CI, không cần cơ sở dữ liệu (trừ ghi chú). Công cụ: pytest (backend), Vitest + Testing Library (frontend).

## Danh sách ca (22)

| Mã ca | Tên |
|---|---|
| [UT-001](UT-001.md) | Trích xuất PDF giữ số trang |
| [UT-002](UT-002.md) | Chuẩn hóa tiếng Việt về NFC |
| [UT-003](UT-003.md) | Phân loại lỗi PDF |
| [UT-004](UT-004.md) | Chunk không vượt ranh giới trang |
| [UT-005](UT-005.md) | Trang ngắn và trang rỗng |
| [UT-006](UT-006.md) | Giới hạn token, chồng lấp và ghép lại văn bản |
| [UT-007](UT-007.md) | Lớp từ chối 1: dưới ngưỡng không gọi mô hình |
| [UT-008](UT-008.md) | Lớp từ chối 2: câu từ chối cố định |
| [UT-009](UT-009.md) | Lớp từ chối 3: có nội dung nhưng không có nguồn hợp lệ |
| [UT-010](UT-010.md) | Ánh xạ và gộp citation |
| [UT-011](UT-011.md) | Ghép câu hỏi trước vào truy vấn |
| [UT-012](UT-012.md) | Adapter Claude: ánh xạ citation |
| [UT-013](UT-013.md) | Adapter Claude: từ chối và cắt cụt |
| [UT-014](UT-014.md) | Adapter Claude: hình dạng yêu cầu |
| [UT-015](UT-015.md) | Adapter OIDC: kiểm tra ID token |
| [UT-016](UT-016.md) | Định dạng lỗi chung, không lộ chi tiết kỹ thuật |
| [UT-017](UT-017.md) | Log không chứa nội dung câu hỏi |
| [UT-018](UT-018.md) | Tiến trình API nạp đủ model |
| [UT-019](UT-019.md) | Mọi ngưỡng là trường cấu hình |
| [UT-020](UT-020.md) | Bảng thông báo lỗi tải lên |
| [UT-021](UT-021.md) | Tô sáng đoạn trích trong trang nguồn |
| [UT-022](UT-022.md) | Công thức chỉ số của bộ đánh giá |
