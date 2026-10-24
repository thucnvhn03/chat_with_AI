# 04 — Ca kiểm thử chấp nhận (UAT-001..UAT-011)

Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md) mục 6.1.4. Môi trường: Test/Staging với Claude thật và embedding `bge-m3`, dữ liệu thật được phép theo OQ-005. Thực hiện **thủ công** bởi người dùng BD, quản lý, quản trị bảo mật, business owner, cùng QA ghi kết quả.

**Điều kiện vào chung:** kiểm thử hệ thống đạt; cổng G3 đã qua (OQ-002 chốt ngưỡng; có PDF thật và bộ câu hỏi chuẩn — DEP-001, ASM-005); tài khoản thật được cấp quyền.

**Ghi kết quả:** Đạt / Không đạt, người thực hiện, ngày, ghi chú, mã lỗi (nếu có). Mỗi ca "Không đạt" phải có lỗi ghi nhận và người chịu trách nhiệm.

## Danh sách ca (11)

| Mã ca | Tên |
|---|---|
| [UAT-001](UAT-001.md) | Tải nhiều PDF thật |
| [UAT-002](UAT-002.md) | Tệp lỗi có lý do dễ hiểu |
| [UAT-003](UAT-003.md) | Trả lời câu hỏi thường gặp có nguồn |
| [UAT-004](UAT-004.md) | Không bịa khi tài liệu không có thông tin |
| [UAT-005](UAT-005.md) | Hỏi tiếp bằng đại từ |
| [UAT-006](UAT-006.md) | Xóa tài liệu và xác nhận xóa vĩnh viễn |
| [UAT-007](UAT-007.md) | Cấp/thu hồi quyền và cô lập tài liệu |
| [UAT-008](UAT-008.md) | Tra cứu bản ghi kiểm toán |
| [UAT-009](UAT-009.md) | Báo cáo mức sử dụng |
| [UAT-010](UAT-010.md) | Nghiệm thu chất lượng theo ngôn ngữ |
| [UAT-011](UAT-011.md) | Rà soát chính sách dữ liệu |
