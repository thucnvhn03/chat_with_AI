# T1-20 · Kiểm thử tích hợp luồng nạp

| Thuộc tính | Giá trị |
|---|---|
| Sprint | 1 — Truy cập và nạp tài liệu |
| Story | US-001 — Tải một file PDF lên (P0); US-002 — Tải nhiều PDF vào cùng một tập tài liệu (P0); US-003 — Biết file nào tải thất bại (P0); US-004 — Biết lý do tệp thất bại (P1); US-005 — Xem danh sách tài liệu đã tải (P1) |
| Loại việc | QA |
| Cỡ | M (tương đối: S ≈ vài ngày-người, M ≈ một tuần-người, L > một tuần-người) |
| Phụ thuộc | T1-15, T1-16 |
| Trạng thái | Review (mã và kiểm thử tự động xong, chạy xanh; chờ rà soát mã) |

- **Làm gì:** bộ kiểm thử tích hợp gọi API thật + worker thật + PostgreSQL/MinIO thật bằng bộ PDF tổng hợp: tải một tệp, tải nhiều tệp, từng loại lỗi, hai worker đồng thời, thử lại. Thêm kiểm thử vòng đời: mọi tài liệu `ready` có ≥ 1 chunk và mọi chunk có `page` hợp lệ (1..`page_count`).
- **Xong khi:** phủ AC-001, AC-002, AC-003, AC-004, AC-018; chạy trong CI dưới thời gian cho phép [Đề xuất: 5 phút].

---

**Tài liệu liên quan:** [implement_plan.md](../implement_plan.md) · [implement_tasks.md](../implement_tasks.md) · [UserStories.md](../../requirements/UserStories.md) · [giao diện mẫu](../../design/html_design/index.html)

**Cổng quyết định của sprint:** không có

**Định nghĩa hoàn thành chung** (áp dụng cho mọi task): mọi điều kiện "Xong khi" đạt; AC liên quan có kiểm thử tự động; giao diện khớp ảnh màn hình mẫu và đạt kiểm tra khả năng tiếp cận; không viết cứng ngưỡng; log và sự kiện không chứa nội dung tài liệu/câu hỏi; mã được rà soát và CI xanh. Chi tiết ở cuối [implement_tasks.md](../implement_tasks.md).
