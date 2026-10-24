# T1-18 · FE: danh sách tài liệu, trạng thái, lỗi, trạng thái trống

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-001 — Tải một file PDF lên (P0); US-003 — Biết file nào tải thất bại (P0); US-005 — Xem danh sách tài liệu đã tải (P1) |
| Loại việc | FE |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-16, T1-17 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** `DocumentList` (C-04) và `StatusBadge` (C-06) khớp ảnh `s02-default` và `s02-empty`: tên, số trang, dung lượng, nhãn Sẵn sàng/Đang xử lý/Lỗi; tệp lỗi có lý do, nút Thử lại và Xóa (nút Xóa nối vào T3-01). Hỏi trạng thái mỗi `POLL_INTERVAL_S` khi còn tài liệu `processing`, dừng khi không còn. Trạng thái trống (C-10) hướng dẫn tải PDF.
- **Xong khi:** kiểm thử cho ba trạng thái; hỏi định kỳ dừng khi không còn tài liệu đang xử lý; danh sách 200 mục không giật (ảo hóa nếu cần).

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
