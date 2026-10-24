# 07 — Ca kiểm thử khả năng tiếp cận (ACC-001..ACC-008)

Kế hoạch: [Master_Test_Plan.md](../../Master_Test_Plan.md) mục 6.1.8. Chuẩn: WCAG 2.1 AA [Đề xuất, chờ DQ-004]. Môi trường: cấu hình E2E. Công cụ: @axe-core/playwright (trình duyệt thật, có kiểm tương phản), axe-core trong Vitest (jsdom, **không** kiểm tương phản), NVDA (Windows + Chrome) và VoiceOver (macOS + Safari) cho ca thủ công.

Mức chấp nhận: không có vi phạm mức nghiêm trọng hoặc cao; vi phạm nhỏ còn lại có người chịu trách nhiệm và hạn (T4-08).

## Danh sách ca (8)

| Mã ca | Tên |
|---|---|
| [ACC-001](ACC-001.md) | Dùng được chỉ bằng bàn phím |
| [ACC-002](ACC-002.md) | Trình đọc màn hình |
| [ACC-003](ACC-003.md) | Tương phản màu |
| [ACC-004](ACC-004.md) | Thuộc tính ARIA |
| [ACC-005](ACC-005.md) | Quản lý tiêu điểm |
| [ACC-006](ACC-006.md) | Thông báo lỗi được trình đọc màn hình nhận |
| [ACC-007](ACC-007.md) | Thu phóng 200% |
| [ACC-008](ACC-008.md) | Không chỉ dùng màu để truyền thông tin |
